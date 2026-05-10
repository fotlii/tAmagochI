"""
Desktop AI Lifeform — LLM Interface (llm.py)
=============================================
Optional Ollama integration for generating short ambient thoughts
and discerning emotional states. Now in Spanish.
"""

import asyncio
import json
import logging
import random
from typing import Optional, List

from backend import config

logger = logging.getLogger(__name__)

# Frases de respaldo en español
FALLBACK_PHRASES = {
	"idle": ["...", "sigo aquí", "qué día más tranquilo", "esperando...", "hmm"],
	"sleeping": ["zzz", "soñando con bits", "...", "ruido suave"],
	"curious": ["¿ah?", "¿qué es eso?", "algo nuevo", "interesante", "me he fijado en eso"],
	"focused": ["no rompas el flujo", "concentrado...", "procesando", "ya casi está", "hiperenfoque"],
	"stressed": ["demasiadas cosas", "necesito calma", "error", "sobrecarga", "respira"],
	"lonely": ["¿a dónde has ido?", "solo otra vez", "esperando", "vuelve", "..."],
	"happy": ["buenas vibras", "esto me gusta", "calentito", "me siento bien"],
	"gaming": ["gg", "concentrado en la partida", "jugando", "diversión"],
	"watching": ["buena escena", "está interesante", "shhh", "palomitas digitales", "mirando"],
}


async def generate_thought(
	state: str,
	vars_dict: dict,
	recent_phrases: list,
	memory_context: Optional[str] = None,
) -> Optional[str]:
	if random.random() > config.LLM_PHRASE_CHANCE:
		return None

	if config.LLM_ENABLED:
		phrase = await _call_ollama_thought(state, vars_dict, recent_phrases)
		if phrase:
			return phrase

	pool = FALLBACK_PHRASES.get(state, FALLBACK_PHRASES["idle"])
	available = [p for p in pool if p not in recent_phrases]
	if not available:
		available = pool
	return random.choice(available)


async def discern_state(
	vars_dict: dict,
	idle_seconds: float,
	current_window_class: str,
	current_window_title: str,
) -> Optional[str]:
	if not config.LLM_ENABLED:
		return None

	states = [rule[0] for rule in config.STATE_RULES if rule[0] != "idle"]
	states_str = ", ".join(states)

	prompt = (
		f"Context: {vars_dict}. Idle time: {idle_seconds}s. "
		f"Active Window: '{current_window_title}' (class: {current_window_class}). "
		f"Available states: {states_str}, idle. "
		f"Instruction: Pick the ONE state that best describes the USER'S CURRENT activity. "
		f"If class is 'music', prioritize 'happy'. "
		f"If class is 'terminal' or 'code', prioritize 'focused' or 'idle'. "
		f"Reply with ONLY the state name, lowercase."
	)

	payload = {
		"model": config.LLM_MODEL,
		"prompt": prompt,
		"stream": False,
		"options": {"temperature": 0.3, "num_predict": 10},
	}

	try:
		import aiohttp
		async with aiohttp.ClientSession() as session:
			async with session.post(
				f"{config.LLM_OLLAMA_URL}/api/generate",
				json=payload,
				timeout=aiohttp.ClientTimeout(total=5),
			) as resp:
				if resp.status == 200:
					data = await resp.json()
					state = data.get("response", "").strip().lower()
					valid = [s for s in states] + ["idle"]
					for s in valid:
						if s in state: return s
	except Exception:
		pass
	return None


async def _call_ollama_thought(
	state: str,
	vars: dict,
	recent_phrases: list,
) -> Optional[str]:
	try:
		import aiohttp
	except ImportError:
		return None

	avoid = ", ".join(f'"{p}"' for p in recent_phrases[-5:]) if recent_phrases else "ninguna"
	
	# Prompt updated to request Spanish
	prompt = (
		f"Eres una pequeña criatura digital viviendo en una pantalla. "
		f"Estado actual: {state}. Variables: {vars}. "
		f"Genera UN pensamiento corto en ESPAÑOL (máximo 5 palabras). "
		f"Evita: {avoid}. Estilo: tranquilo, algo críptico, sin comillas ni puntuación excesiva."
	)

	payload = {
		"model": config.LLM_MODEL,
		"prompt": prompt,
		"stream": False,
		"options": {"temperature": 0.8, "num_predict": 20},
	}

	try:
		async with aiohttp.ClientSession() as session:
			async with session.post(
				f"{config.LLM_OLLAMA_URL}/api/generate",
				json=payload,
				timeout=aiohttp.ClientTimeout(total=5),
			) as resp:
				if resp.status == 200:
					data = await resp.json()
					return data.get("response", "").strip().replace('"', '')
	except Exception:
		pass
	return None
