# Installation Guide

## Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Godot | 4.3+ | [godotengine.org](https://godotengine.org/download) |
| Windows | 10/11 | pywin32 required for window detection |
| Ollama | latest | Optional — for LLM phrases |

---

## Step 1: Clone / Download

```
Place project folder at any location, e.g.:
  C:\Users\YourName\Desktop\Desktop-AI-Lifeform\
```

---

## Step 2: Python Backend

### Option A: Auto (double-click)
Run `run_backend.bat` — it creates a `.venv` automatically.

### Option B: Manual

```powershell
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Dependencies installed:**
- `websockets` — WebSocket server
- `psutil` — CPU/RAM/process monitoring
- `pywin32` — Windows active window detection
- `pynput` — keyboard/mouse idle tracking
- `aiohttp` — for optional Ollama LLM calls

---

## Step 3: Godot Frontend

1. Download [Godot 4.3+](https://godotengine.org/download) (standard, not Mono)
2. Launch Godot
3. Click **Import** → navigate to `frontend/project.godot`
4. Click **Import & Edit**

### To run on mini display:
1. Project → Project Settings → Display → Window
2. Set **Initial Position** to match your secondary screen coordinates
3. Enable **Always On Top** and **Borderless**
4. Run with F5

### To export as standalone:
1. Project → Export → Add Preset → Windows Desktop
2. Export to `dist/lifeform.exe`

---

## Step 4: Add Sprite Assets

The creature needs pixel art sprites. Place the sprite sheet at:
```
frontend/assets/sprites/creature_sheet.png
```

The sheet should be a **PNG with transparency**, with frames arranged horizontally
or as a grid. The `SpriteFrames` resource in `creature.tscn` references this file.

**Recommended frame size:** 64×64 px per frame  
**Recommended sheet size:** 384×128 px (6 states × 2 frames)

States needed (in order):
1. idle (2 frames: breathe in / breathe out)
2. blink (2 frames: half / closed)
3. sleep (2 frames: closed / zzz)
4. curious (2 frames: wide / tilt)
5. focused (2 frames: narrow / intense)
6. stressed (2 frames: normal / glitch)
7. lonely (1 frame: droop)

---

## Step 5: Optional — Ollama LLM

```powershell
# Install Ollama: https://ollama.com
# Pull a small model
ollama pull llama3.2:1b

# Enable in config.py
LLM_ENABLED = True
```

---

## Running

### Terminal (recommended for first run):
```powershell
cd C:\path\to\project
.venv\Scripts\activate
python -m backend.main
```

### Then open Godot and press F5.

### Or use the batch scripts:
- `run_backend.bat` — starts the Python daemon
- `run_frontend.bat` — launches Godot (if installed in standard paths)

---

## Auto-start at Windows Login (optional)

1. Press `Win + R` → type `shell:startup`
2. Create a shortcut to `run_backend.bat` in that folder
3. The daemon will start silently with Windows

For a completely silent background start, create a `.vbs` wrapper:
```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c C:\path\to\run_backend.bat", 0, False
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: psutil` | Run `pip install -r requirements.txt` |
| `pywin32 not found` | Run `pip install pywin32` |
| Godot shows black screen | Check `project.godot` transparent window settings |
| WebSocket refused | Make sure backend is running first |
| No thoughts shown | Set `LLM_ENABLED=False` in config.py (or install Ollama) |
| Creature not blinking | Check `creature_sheet.png` exists in `frontend/assets/sprites/` |
