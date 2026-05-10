"""
Desktop AI Lifeform — Input Sensor (input_sensor.py)
=====================================================
Listens to keyboard and mouse activity via pynput.
Tracks idle time and typing bursts without capturing
actual keystrokes (only event presence/absence).

Privacy-first: no keys are recorded, only timestamps.
"""

import asyncio
import logging
import time
import threading
from typing import Callable

from backend import config

logger = logging.getLogger(__name__)

try:
    from pynput import keyboard, mouse
    _PYNPUT_AVAILABLE = True
except ImportError:
    _PYNPUT_AVAILABLE = False
    logger.warning("pynput not available — InputSensor running in stub mode")


class InputSensor:
    """
    Tracks user input activity to compute idle time.
    Fires stimuli when the user has been idle for a while.

    Runs pynput listeners in a background thread; reports
    idle seconds to the creature via asyncio-safe callbacks.
    """

    def __init__(self, on_stimulus: Callable[[str, float], None]):
        self._on_stimulus = on_stimulus
        self._last_activity: float = time.monotonic()
        self._running = False
        self._kb_listener = None
        self._mouse_listener = None
        self._idle_notified_lonely = False
        self._idle_notified_sleep = False

    def idle_seconds(self) -> float:
        return time.monotonic() - self._last_activity

    def _on_activity(self):
        """Called on any keyboard or mouse event."""
        was_idle = self.idle_seconds()
        self._last_activity = time.monotonic()

        # Reset idle notifications
        if was_idle > config.IDLE_LONELY_THRESHOLD_S:
            self._idle_notified_lonely = False
        if was_idle > config.IDLE_SLEEP_THRESHOLD_S:
            self._idle_notified_sleep = False

    def start(self):
        """Start pynput listeners in background threads."""
        if not _PYNPUT_AVAILABLE:
            logger.warning("InputSensor: pynput not available, idle detection disabled")
            return

        self._running = True

        # Keyboard listener — only tracks presence, not content
        self._kb_listener = keyboard.Listener(
            on_press=lambda _: self._on_activity()
        )
        self._kb_listener.daemon = True
        self._kb_listener.start()

        # Mouse listener
        self._mouse_listener = mouse.Listener(
            on_move=lambda x, y: self._on_activity(),
            on_click=lambda x, y, b, p: self._on_activity(),
            on_scroll=lambda x, y, dx, dy: self._on_activity(),
        )
        self._mouse_listener.daemon = True
        self._mouse_listener.start()

        logger.info("InputSensor started")

    def stop(self):
        self._running = False
        if self._kb_listener:
            self._kb_listener.stop()
        if self._mouse_listener:
            self._mouse_listener.stop()

    async def check_idle_loop(self):
        """
        Async loop: periodically checks idle duration and fires stimuli.
        Call this from the main asyncio loop.
        """
        while True:
            idle = self.idle_seconds()

            # Lonely threshold
            if idle > config.IDLE_LONELY_THRESHOLD_S and not self._idle_notified_lonely:
                self._on_stimulus("idle_long", min(1.0, idle / config.IDLE_SLEEP_THRESHOLD_S))
                self._idle_notified_lonely = True
                logger.debug(f"Idle {idle:.0f}s → idle_long stimulus")

            # Sleep threshold
            if idle > config.IDLE_SLEEP_THRESHOLD_S and not self._idle_notified_sleep:
                self._on_stimulus("idle_short", 0.3)
                self._idle_notified_sleep = True
                logger.debug(f"Idle {idle:.0f}s → sleep stimulus")

            await asyncio.sleep(30)   # check every 30s
