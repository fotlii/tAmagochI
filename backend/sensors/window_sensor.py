"""
Desktop AI Lifeform — Window Sensor (window_sensor.py)
=======================================================
Watches the active foreground window title and classifies it into
abstract app categories. Fires stimuli when the user switches contexts.

Uses win32gui on Windows (part of pywin32). Falls back gracefully
to a stub on non-Windows systems.
"""

import asyncio
import logging
import time
from typing import Callable, Optional, Tuple

from backend import config

logger = logging.getLogger(__name__)

# Try to import win32gui; stub if unavailable
try:
    import win32gui
    import win32process
    import psutil as _psutil
    _WIN32_AVAILABLE = True
except ImportError:
    _WIN32_AVAILABLE = False
    logger.warning("pywin32 not available — WindowSensor running in stub mode")


class WindowSensor:
    """
    Polls the active window every SENSOR_INTERVAL_S.
    Classifies it by app category and fires stimuli on transitions.
    Also tracks time spent per category to detect coding sessions, etc.
    """

    def __init__(
        self,
        on_stimulus: Callable[[str, float], None],
        on_window_change: Callable[[str, str], None],
    ):
        """
        Args:
            on_stimulus:      callback(stimulus_name, intensity)
            on_window_change: callback(window_title, app_class) on focus change
        """
        self._on_stimulus = on_stimulus
        self._on_window_change = on_window_change
        self._running = False
        self._prev_title: str = ""
        self._prev_class: str = "unknown"
        # Time tracker per class: {class: seconds_spent}
        self._time_in_class: dict = {}
        self._class_session_start: float = time.monotonic()
        # How many distinct classes seen this session (variety metric)
        self._classes_seen: set = set()

    async def start(self):
        self._running = True
        logger.info("WindowSensor started")
        while self._running:
            try:
                await self._sample()
            except Exception as e:
                logger.warning(f"WindowSensor sample error: {e}")
            await asyncio.sleep(config.SENSOR_INTERVAL_S)

    def stop(self):
        self._running = False

    def current_app_class(self) -> str:
        return self._prev_class

    async def _sample(self):
        title, exe = _get_active_window()
        if not title and not exe:
            return

        app_class = _classify_window(title, exe)

        # ── Track variety (social_energy) ─────────────────────────────────
        self._classes_seen.add(app_class)
        if len(self._classes_seen) >= 3:
            # Varied activity → social energy boost
            self._on_stimulus("varied_activity", 0.5)
            self._classes_seen.clear()

        # ── Detect class transition ────────────────────────────────────────
        if title != self._prev_title:
            # Accumulate time for previous class
            elapsed = time.monotonic() - self._class_session_start
            self._time_in_class[self._prev_class] = (
                self._time_in_class.get(self._prev_class, 0.0) + elapsed
            )
            self._class_session_start = time.monotonic()

            # Check if previous coding session was long
            if self._prev_class == "code":
                coding_minutes = self._time_in_class.get("code", 0) / 60
                if coding_minutes > 30:
                    intensity = min(1.0, coding_minutes / 90)
                    self._on_stimulus("coding_session", intensity)
                    logger.debug(f"Long coding session: {coding_minutes:.0f}min")

            # Fire new-app stimulus on transitions to novel classes
            if app_class != self._prev_class:
                self._on_stimulus("new_app", 0.7)
                logger.info(f"Window: '{title[:40]}' → class='{app_class}'")

            self._on_window_change(title, app_class)
            self._prev_title = title
            self._prev_class = app_class

        # ── Detect AI chat (boosts social energy) ─────────────────────────
        if app_class == "ai_chat":
            ai_minutes = self._time_in_class.get("ai_chat", 0.0) / 60
            if ai_minutes > 10:
                self._on_stimulus("long_ai_chat", min(1.0, ai_minutes / 30))

        # ── Music detection ───────────────────────────────────────────────
        if app_class == "music":
            # Adjusted boost to be stronger than decay, so it can reach 'happy'
            self._on_stimulus("music", 0.4)


# ── Window helpers ─────────────────────────────────────────────────────────────

def _get_active_window() -> Tuple[str, str]:
    """Returns (window_title, exe_name). Empty strings if unavailable."""
    if not _WIN32_AVAILABLE:
        return "", ""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd) or ""
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            proc = _psutil.Process(pid)
            exe = proc.name().lower()
        except Exception:
            exe = ""
        return title.lower(), exe
    except Exception:
        return "", ""


def _classify_window(title: str, exe: str) -> str:
    """Classify a window into one of the defined app categories."""
    combined = f"{title} {exe}"
    for category, keywords in config.WINDOW_CLASSES.items():
        if any(kw in combined for kw in keywords):
            return category
    return "other"
