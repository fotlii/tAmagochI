"""
Desktop AI Lifeform — System Sensor (system_sensor.py)
=======================================================
Monitors CPU, RAM, process list, and system-level events.
Translates raw numbers into abstract stimuli — never exposes
raw percentages to the creature or the UI.
"""

import asyncio
import logging
import time
from typing import Callable, Dict, List, Optional

import psutil

from backend import config

logger = logging.getLogger(__name__)


class SystemSensor:
    """
    Samples system state periodically and fires stimuli callbacks
    when notable conditions are detected.
    """

    def __init__(self, on_stimulus: Callable[[str, float], None], on_stats: Optional[Callable[[float, float], None]] = None):
        """
        Args:
            on_stimulus: callback(stimulus_name, intensity)
            on_stats:    callback(cpu_percent, ram_percent)
        """
        self._on_stimulus = on_stimulus
        self._on_stats = on_stats
        self._running = False
        self._prev_cpu: float = 0.0
        self._prev_processes: set = set()
        self._session_start: float = time.monotonic()
        self._high_cpu_streak: int = 0  # consecutive high-CPU samples

    async def start(self):
        """Run the sensor loop until stopped."""
        self._running = True
        logger.info("SystemSensor started")
        while self._running:
            try:
                await self._sample()
            except Exception as e:
                logger.warning(f"SystemSensor sample error: {e}")
            await asyncio.sleep(config.SENSOR_INTERVAL_S)

    def stop(self):
        self._running = False

    async def _sample(self):
        # ── CPU ────────────────────────────────────────────────────────────
        # Use a short interval to not block the event loop
        cpu = await asyncio.get_event_loop().run_in_executor(
            None, lambda: psutil.cpu_percent(interval=0.5)
        )
        self._prev_cpu = cpu

        if cpu > 85:
            self._high_cpu_streak += 1
        else:
            self._high_cpu_streak = 0

        # Sustained high CPU → stress
        if self._high_cpu_streak >= 3:
            intensity = _normalize(cpu, 70, 100)
            self._on_stimulus("system_crash", intensity * 0.6)
            logger.debug(f"High CPU streak: {cpu:.0f}% → stress stimulus")

        # ── RAM ────────────────────────────────────────────────────────────
        ram = psutil.virtual_memory()
        ram_pct = ram.percent
        if ram_pct > 88:
            intensity = _normalize(ram_pct, 80, 100)
            self._on_stimulus("many_tabs", intensity * 0.5)

        # ── Broadcast Stats ────────────────────────────────────────────────
        if self._on_stats:
            self._on_stats(cpu, ram_pct)

        # ── Process list — detect new interesting processes ─────────────────
        current_procs = {
            p.info["name"].lower()
            for p in psutil.process_iter(["name"])
            if p.info["name"]
        }

        new_procs = current_procs - self._prev_processes
        for proc_name in new_procs:
            stimulus = _classify_process(proc_name)
            if stimulus:
                logger.debug(f"New process '{proc_name}' → stimulus '{stimulus}'")
                self._on_stimulus(stimulus, 0.6)

        self._prev_processes = current_procs

        # ── Long session awareness ─────────────────────────────────────────
        session_minutes = (time.monotonic() - self._session_start) / 60
        if session_minutes > 120:
            # 2+ hour session → building fatigue
            intensity = min(1.0, (session_minutes - 120) / 240)
            self._on_stimulus("idle_long", intensity * 0.3)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _normalize(value: float, lo: float, hi: float) -> float:
    """Map value in [lo, hi] to [0, 1]."""
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


# Known process patterns → stimuli
_PROCESS_STIMULI: Dict[str, str] = {
    # Build tools → coding activity
    "msbuild": "coding_session",
    "cargo":   "coding_session",
    "gcc":     "coding_session",
    "clang":   "coding_session",
    "python":  "coding_session",
    "node":    "coding_session",
    "go":      "coding_session",
    "gradle":  "coding_session",
    "mvn":     "coding_session",
    # Music players → relaxation
    "spotify": "music",
    "vlc":     "music",
    "foobar2000": "music",
    # Games → fun stimulus
    "steam":   "game",
}


def _classify_process(name: str) -> Optional[str]:
    for key, stimulus in _PROCESS_STIMULI.items():
        if key in name:
            return stimulus
    return None
