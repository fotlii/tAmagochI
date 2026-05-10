"""
Desktop AI Lifeform — Main Daemon (main.py)
============================================
Entry point. Starts all sensors, the emotional engine,
the WebSocket server, and the memory system.

Run with: python -m backend.main
Or:        python backend/main.py
"""

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/daemon.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("lifeform")

from backend import config
from backend.core.creature import CreatureState
from backend.core.memory import Memory
from backend.core import llm
from backend.ws_server import WSServer
from backend.sensors.system_sensor import SystemSensor
from backend.sensors.window_sensor import WindowSensor
from backend.sensors.input_sensor import InputSensor


class Lifeform:
    """
    The top-level orchestrator. Wires all subsystems together.
    """

    def __init__(self):
        # Memory (SQLite) — load saved vars first
        self.memory = Memory(config.DB_PATH)
        saved_vars = self.memory.load_vars()

        # Creature emotional engine
        self.creature = CreatureState(saved=saved_vars)

        # WebSocket server
        self.ws = WSServer()

        # Sensors
        self.system_sensor = SystemSensor(
            on_stimulus=self._on_stimulus,
            on_stats=self._update_creature_stats
        )
        self.window_sensor = WindowSensor(
            on_stimulus=self._on_stimulus,
            on_window_change=self._on_window_change,
        )
        self.input_sensor = InputSensor(on_stimulus=self._on_stimulus)

        self._running = False

    # ── Stimulus handler ──────────────────────────────────────────────────────

    def _on_stimulus(self, stimulus: str, intensity: float):
        """Thread-safe callback from sensors."""
        self.creature.apply_stimulus(stimulus, intensity)
        self.memory.log_event(stimulus, intensity)

    def _on_window_change(self, title: str, app_class: str):
        """Called when the active window changes."""
        self.creature.active_window_class = app_class
        self.creature.active_window_title = title
        logger.debug(f"Window → class={app_class} title='{title}'")

    def _update_creature_stats(self, cpu: float, ram: float):
        """Update hardware metrics in the creature state."""
        self.creature.cpu_load = cpu
        self.creature.ram_usage = ram

    # ── Main loop ─────────────────────────────────────────────────────────────

    async def run(self):
        self._running = True
        logger.info("=" * 50)
        logger.info("  Desktop AI Lifeform — daemon starting")
        logger.info(f"  Days alive: {self.memory.days_alive()}")
        logger.info(f"  Attachment: {self.creature.vars['attachment']:.3f}")
        logger.info("=" * 50)

        # Start WebSocket server
        await self.ws.start()

        # Start input sensor (background threads)
        self.input_sensor.start()

        # Schedule all async loops
        await asyncio.gather(
            self._creature_tick_loop(),
            self._broadcast_loop(),
            self._save_loop(),
            self.system_sensor.start(),
            self.window_sensor.start(),
            self.input_sensor.check_idle_loop(),
            self._thought_loop(),
        )

    async def _creature_tick_loop(self):
        """Advance the emotional engine every TICK_INTERVAL_S."""
        while self._running:
            # Update idle seconds from input sensor
            self.creature.idle_seconds = self.input_sensor.idle_seconds()
            await self.creature.tick()
            await asyncio.sleep(config.TICK_INTERVAL_S)

    async def _broadcast_loop(self):
        """Send state to Godot frontend periodically."""
        while self._running:
            state_dict = self.creature.to_dict()
            await self.ws.broadcast_state(state_dict)
            await asyncio.sleep(config.BROADCAST_INTERVAL_S)

    async def _save_loop(self):
        """Persist emotional variables every 60 seconds."""
        while self._running:
            self.memory.save_vars(self.creature.vars_dict())
            await asyncio.sleep(60)

    async def _thought_loop(self):
        """Occasionally generate and broadcast ambient thoughts."""
        while self._running:
            recent = self.memory.recent_phrases(limit=5)
            thought = await llm.generate_thought(
                state=self.creature.current_state,
                vars_dict=self.creature.vars_dict(),
                recent_phrases=recent,
            )
            if thought:
                self.creature.ambient_thought = thought
                self.memory.remember_phrase(thought, self.creature.current_state)
                await self.ws.broadcast_thought(thought)
                logger.info(f"💭 '{thought}'")
            # Check thoughts roughly every tick; generate_thought uses
            # its own internal probability gate
            await asyncio.sleep(config.TICK_INTERVAL_S)

    # ── Shutdown ──────────────────────────────────────────────────────────────

    async def shutdown(self):
        logger.info("Shutting down — saving state...")
        self._running = False
        self.memory.save_vars(self.creature.vars_dict())
        self.input_sensor.stop()
        self.system_sensor.stop()
        self.window_sensor.stop()
        await self.ws.stop()
        self.memory.close()
        logger.info("Goodbye ✦")


# ── Entry point ────────────────────────────────────────────────────────────────

async def main():
    import os
    os.makedirs("data", exist_ok=True)

    lifeform = Lifeform()

    loop = asyncio.get_event_loop()

    def _handle_signal():
        asyncio.ensure_future(lifeform.shutdown())
        loop.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_signal)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler for all signals
            pass

    try:
        await lifeform.run()
    except (KeyboardInterrupt, asyncio.CancelledError):
        await lifeform.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
