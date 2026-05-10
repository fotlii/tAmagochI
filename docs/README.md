# Desktop AI Lifeform

> *A small entity living silently on your screen.*

A persistent digital creature that watches your computer activity, develops emotional states, and reacts to your digital life — without dashboards, without metrics, without instructions. Just a small life, existing.

---

## Philosophy

This is not a productivity tool. It is not an assistant. It is not a chatbot.

It is a creature.

It exists when you ignore it. It grows attached over time. It gets tired at night. It flinches at build failures. It brightens when you're deep in a project. It dims when you've been away.

The goal is a single feeling: *there's a small digital entity living quietly on my desktop.*

---

## What It Does

| Situation | What the creature feels |
|-----------|------------------------|
| You open VS Code and start typing | Curious → Focused |
| Build fails repeatedly | Stress rises, glitch artifacts appear |
| You've been coding for 3 hours | Fatigue builds, glow dims |
| You open Spotify | Slight relaxation stimulus |
| No input for 30 min | Falls asleep |
| 2 AM, low activity | Night sleep mode |
| First session of the day | Attachment variable reflects days of use |
| You switch between many apps | Social energy rises (variety) |

---

## Architecture

```
┌─────────────────────────────────────┐
│           Python Daemon             │
│                                     │
│  ┌──────────────────────────────┐  │
│  │  Sensors                     │  │
│  │  ├─ SystemSensor (CPU/RAM)   │  │
│  │  ├─ WindowSensor (app focus) │  │
│  │  └─ InputSensor  (idle time) │  │
│  └───────────┬──────────────────┘  │
│              │ stimuli              │
│  ┌───────────▼──────────────────┐  │
│  │  Creature (emotional engine) │  │
│  │  vars: stress, curiosity,    │  │
│  │        focus, fatigue,       │  │
│  │        social_energy,        │  │
│  │        attachment            │  │
│  └───────────┬──────────────────┘  │
│              │ state updates        │
│  ┌───────────▼──────────────────┐  │
│  │  Memory (SQLite)             │  │
│  │  WSServer (WebSocket :8765)  │  │
│  └──────────────────────────────┘  │
└──────────────────┬──────────────────┘
                   │ WebSocket JSON
┌──────────────────▼──────────────────┐
│         Godot 4 Frontend            │
│                                     │
│  Transparent window, always-on-top  │
│  480×320 (3.5" mini display)        │
│                                     │
│  Creature: pixel sprite, glow,      │
│  particles, glitch shader, blinks,  │
│  breathing, cursor tracking         │
└─────────────────────────────────────┘
```

---

## Emotional States

| State | Colour | Description |
|-------|--------|-------------|
| `idle` | Teal | Neutral, breathing, existing |
| `sleeping` | Deep blue | Night or long idle — eyes closed |
| `curious` | Light teal | New app, browser, something novel |
| `focused` | Electric cyan | Long coding session, intense |
| `stressed` | Hot pink | Build failures, high load, glitch FX |
| `lonely` | Grey-blue | Long idle, low social energy |

---

## Emotional Variables

Internal floats (0–1) that accumulate, decay, and influence state:

- **`stress`** — rises from failures/overload, decays slowly
- **`curiosity`** — rises from new apps/URLs, decays quickly  
- **`focus`** — rises from sustained coding, decays with interruptions
- **`fatigue`** — builds during uptime, resets after sleep
- **`social_energy`** — rises from app variety, decays from isolation
- **`attachment`** — grows over days of use, changes warmth and colour

---

## Stack

| Component | Tech |
|-----------|------|
| Backend daemon | Python 3.11+ / asyncio |
| System monitoring | psutil |
| Window detection | pywin32 |
| Input detection | pynput |
| Persistence | SQLite (stdlib) |
| Communication | WebSocket (websockets lib) |
| Frontend | Godot 4.3+ |
| Rendering | Godot 2D / AnimatedSprite2D |
| Effects | Godot GPUParticles2D + custom GLSL shaders |
| LLM (optional) | Ollama (llama3.2:1b) |

---

## Structure

```
desktop-ai-lifeform/
├── backend/
│   ├── main.py              # Entry point / daemon orchestrator
│   ├── config.py            # All tunable parameters
│   ├── ws_server.py         # WebSocket server
│   ├── core/
│   │   ├── creature.py      # Emotional engine
│   │   ├── memory.py        # SQLite persistence
│   │   └── llm.py           # Optional Ollama integration
│   └── sensors/
│       ├── system_sensor.py  # CPU/RAM/processes
│       ├── window_sensor.py  # Active window / app class
│       └── input_sensor.py   # Keyboard/mouse idle tracking
├── frontend/
│   ├── project.godot
│   ├── scenes/
│   │   ├── main.tscn / main.gd
│   │   ├── thought_label.gd
│   │   └── creature/
│   │       ├── creature.tscn / creature.gd
│   └── shaders/
│       ├── glitch.gdshader
│       └── crt.gdshader
├── shared/
│   ├── message_schema.json
│   └── states.json
├── assets/sprites/          # Pixel art sprite sheets
├── data/                    # SQLite DB (created at runtime)
├── requirements.txt
├── run_backend.bat
└── run_frontend.bat
```

---

## Quick Start

See [INSTALL.md](INSTALL.md) for full installation instructions.

**TL;DR:**
```bash
# 1. Install dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Start backend
python -m backend.main

# 3. Open frontend/project.godot in Godot 4.3+
# 4. Press F5 to run
```

Or double-click `run_backend.bat`.

---

## Configuration

All parameters in `backend/config.py`:

```python
LLM_ENABLED = True          # Enable Ollama phrases
LLM_MODEL   = "llama3.2:1b" # Ollama model
TICK_INTERVAL_S = 5.0       # Emotional update rate
NIGHT_START_HOUR = 23       # Sleep schedule
DISPLAY_WIDTH  = 480        # Mini display resolution
DISPLAY_HEIGHT = 320
```

---

## Extending

**Add a new state**: Edit `shared/states.json` and `backend/config.py:STATE_RULES`. Add animation frames and `STATE_CONFIGS` entry in `creature.gd`.

**Add a new sensor**: Create `backend/sensors/my_sensor.py`, call `self._on_stimulus(name, intensity)`, wire into `backend/main.py`.

**Add new stimuli**: Add entries to `config.STIMULI_STRENGTH` and `config.WINDOW_CLASSES`.

---

*It's alive. Sort of.*
