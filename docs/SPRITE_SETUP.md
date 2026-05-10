# Sprite Setup Guide

This document explains how to connect your `spritesheet.png` to the Godot animation system. Two approaches are available — pick whichever suits you.

---

## Animation Slot Reference

The creature uses this naming convention in Godot's `SpriteFrames` resource:

| Animation name | Loop | Purpose |
|---|---|---|
| `idle_loop` | ✅ | Default state — breathing, existing |
| `idle_intro` | ❌ | Optional one-shot before idle loop |
| `blink` | ❌ | One-shot blink (timer fires every 3–9 s) |
| `sleep_intro` | ❌ | Settling down animation (plays once) |
| `sleep_loop` | ✅ | Main sleeping loop (Zzz breathing) |
| `curious_intro` | ❌ | Quick reaction when entering curious state |
| `curious_loop` | ✅ | Head-tilt look-around loop |
| `focused_intro` | ❌ | Settling into focus |
| `focused_loop` | ✅ | Intense stare loop |
| `stressed_intro` | ❌ | Onset of stress |
| `stressed_loop` | ✅ | Fidget/glitch loop |
| `lonely_loop` | ✅ | Drooped, dim (falls back to `idle_loop` if empty) |
| `happy_intro` | ❌ | Burst of happiness |
| `happy_loop` | ✅ | Warm, bouncy loop |
| `glitch_loop` | ✅ | Peak stress / corrupted override |

> **Rule**: if an `_intro` animation has 0 frames it is skipped automatically.
> If a `_loop` has 0 frames it falls back to `idle_loop`.
> You only *need* to fill in the loops you care about.

---

## Option A — Fill frames manually in Godot (recommended)

This is the easiest workflow. You assign frames by dragging from the spritesheet grid.

### Steps

1. Open **Godot 4**, import the `frontend/` folder as a project.
2. In the **FileSystem** panel, navigate to `scenes/creature/creature.tscn` and double-click to open it.
3. Select the **Sprite** node (`AnimatedSprite2D`) in the Scene tree.
4. In the **Inspector**, click on the **Sprite Frames** property — the SpriteFrames editor opens at the bottom.
5. In the SpriteFrames editor toolbar, click **"Add frames from sprite sheet"** (grid icon).
6. Select `res://assets/sprites/spritesheet.png`.
7. Set **Horizontal**: how many columns your sheet has, **Vertical**: how many rows.
   - If each frame is 64×64 and the sheet is e.g. 640×896, that's 10 cols × 14 rows.
8. The grid appears. Click individual frames to select them, then click **"Add N frame(s)"**.
9. Make sure the correct animation name is selected in the left panel before adding frames.
10. Repeat for each animation slot.

### Setting loop correctly
In the SpriteFrames editor left panel, each animation has a **loop toggle** (circular arrow icon). Set it to:
- ✅ **loop ON** for all `_loop` animations  
- ❌ **loop OFF** for all `_intro` and `blink`

---

## Option B — Auto-generate with Python tool

The script `tools/generate_spriteframes.py` reads your PNG and generates a Godot `.tres` resource file automatically.

### Steps

```powershell
# From project root
.venv\Scripts\python tools/generate_spriteframes.py
```

The script will:
1. Print your spritesheet dimensions
2. Auto-detect content row Y positions
3. Output frame coordinate suggestions
4. Generate `frontend/assets/sprites/creature_frames.tres`

### Configure the layout

Open `tools/generate_spriteframes.py` and edit the `LAYOUT` dictionary.
Each entry has `row_y` (Y pixel of the row) and `frames` (how many frames to slice):

```python
"idle_loop": {
    "row_y": 42,    # ← Y pixel where idle frames start
    "col_x": 0,
    "frames": 5,
    "fps": 5.0,
    "loop": True,
},
```

Use the auto-detected row output to fill these in. Then re-run the script.

### Import the .tres in Godot

1. Open Godot, go to the creature scene
2. Select the **Sprite** (`AnimatedSprite2D`) node
3. In Inspector, drag `creature_frames.tres` onto the **Sprite Frames** property
4. Done — all animations are pre-wired

---

## Spritesheet row mapping (from your sheet)

Based on visual inspection of `spritesheet.png`, the rows are approximately:

| Row | Animation | Suggested animations to map |
|-----|-----------|----------------------------|
| 1 (top) | IDLE | `idle_loop` (all 5 frames), `blink` (pick 2–3 eyes-closing frames) |
| 2 | CURIOUS | `curious_intro` (first 1–2) + `curious_loop` (remaining) |
| 3 | FOCUSED | `focused_intro` (first 2) + `focused_loop` (remaining) |
| 4 | STRESSED | `stressed_intro` (first 2) + `stressed_loop` (remaining) |
| 5 | SLEEPING | `sleep_intro` (first 3, settling) + `sleep_loop` (last 2–3 with Zzz) |
| 6 | HAPPY | `happy_intro` (first 2) + `happy_loop` (remaining) |
| 7 (bottom) | GLITCH/CORRUPTED | `glitch_loop` (all frames) |

> **Tip**: for `blink`, use 3 frames from the IDLE row where the eyes close — the creature.gd plays them as a one-shot and returns to `idle_loop` automatically.

---

## FPS recommendations

| Animation | Suggested FPS |
|-----------|--------------|
| idle_loop | 4–6 |
| sleep_loop | 2–3 |
| blink | 12–16 |
| curious_loop | 6–8 |
| focused_loop | 4–5 |
| stressed_loop | 8–12 |
| happy_loop | 6–8 |
| glitch_loop | 10–14 |
| Any `_intro` | 7–10 |

---

## Testing in Godot

1. Make sure the Python backend is running (`run_backend.bat`)
2. Press **F5** in Godot
3. Open a terminal — watch for state broadcasts
4. Switch apps, leave PC idle, etc. — the creature reacts within a few seconds

To force a specific state for testing, edit `backend/config.py` temporarily:

```python
# In _resolve_state(), return a hardcoded value:
# return "stressed"
```

Or use the test script:
```powershell
.venv\Scripts\python test_backend.py
```
