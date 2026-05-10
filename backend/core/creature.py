"""
Desktop AI Lifeform — Emotional Engine (creature.py)
=====================================================
The heart of the lifeform. Now supports optional LLM-based state discernment.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Optional

from backend import config
from backend.core import llm

logger = logging.getLogger(__name__)


class CreatureState:
    def __init__(self, saved: Optional[Dict] = None):
        self.vars: Dict[str, float] = {
            "stress":        0.0,
            "curiosity":     0.3,
            "social_energy": 0.5,
            "fatigue":       0.0,
            "focus":         0.0,
            "attachment":    0.0,
        }
        if saved:
            for k, v in saved.items():
                if k in self.vars:
                    self.vars[k] = float(v)

        self.current_state: str = "idle"
        self.previous_state: str = "idle"
        self.state_duration: float = 0.0
        self.idle_seconds: float = 0.0
        self.active_window_class: str = "unknown"
        self.active_window_title: str = "unknown"
        self.cpu_load: float = 0.0
        self.ram_usage: float = 0.0
        self._last_tick: float = time.monotonic()
        self.ambient_thought: Optional[str] = None

    def apply_stimulus(self, stimulus_name: str, intensity: float = 1.0):
        impacts = config.STIMULI_STRENGTH.get(stimulus_name, {})
        for var, delta in impacts.items():
            old = self.vars.get(var, 0.0)
            self.vars[var] = _clamp(old + delta * intensity)

    async def tick(self):
        """Advance the emotional engine. Now asynchronous for LLM calls."""
        now = time.monotonic()
        dt_factor = (now - self._last_tick) / config.TICK_INTERVAL_S
        self._last_tick = now

        # Decay all variables
        for var, rate in config.DECAY.items():
            if var in self.vars:
                self.vars[var] = _clamp(self.vars[var] + rate * dt_factor)

        self.state_duration += config.TICK_INTERVAL_S

        # Resolve state (Rule-based with optional LLM discernment)
        new_state = await self._resolve_state()
        
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_duration = 0.0
            logger.info(f"State transition: {self.previous_state} → {self.current_state}")

    async def _resolve_state(self) -> str:
        """
        Decision engine. Uses hardcoded rules for fast response,
        but can be overridden by LLM for nuance.
        """
        # 1. Immediate Hardcoded Rules (High priority)
        idle = self.idle_seconds
        v = self.vars
        hour = datetime.now().hour
        is_night = hour >= config.NIGHT_START_HOUR or hour < config.NIGHT_END_HOUR

        if idle > config.IDLE_SLEEP_THRESHOLD_S or (is_night and v["fatigue"] > 0.6):
            return "sleeping"
        
        if self.active_window_class == "game":
            return "gaming"
        
        if self.active_window_class == "watching":
            return "watching"

        if v["stress"] > 0.7:
            return "stressed"

        # 2. LLM Discernment (Optional)
        # We only call LLM if enabled and not in a high-priority state
        if config.LLM_ENABLED:
            llm_state = await llm.discern_state(
                vars_dict=self.vars_dict(),
                idle_seconds=self.idle_seconds,
                current_window_class=self.active_window_class,
                current_window_title=self.active_window_title
            )
            if llm_state:
                return llm_state

        # 3. Rule-based Fallback
        if v["focus"] > 0.6: return "focused"
        if v["social_energy"] > 0.75 and v["stress"] < 0.3: return "happy"
        if v["curiosity"] > 0.5: return "curious"
        if v["social_energy"] < 0.2 and idle > config.IDLE_LONELY_THRESHOLD_S: return "lonely"

        return "idle"

    def to_dict(self) -> Dict:
        return {
            "state": self.current_state,
            "previous_state": self.previous_state,
            "state_duration": round(self.state_duration, 1),
            "idle_seconds": round(self.idle_seconds, 1),
            "vars": {k: round(v, 4) for k, v in self.vars.items()},
            "cpu_load": round(self.cpu_load, 2),
            "ram_usage": round(self.ram_usage, 2),
            "ambient_thought": self.ambient_thought,
        }

    def vars_dict(self) -> Dict:
        return {k: round(v, 4) for k, v in self.vars.items()}


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
