"""
Desktop AI Lifeform — Auto-generate Godot SpriteFrames .tres
=============================================================
Uses exact frame coordinates detected from spritesheet.png.
Sheet: 1536x1024  |  Frame size: 64x64  |  8 frames per row

Each animation row has 8 frames. The gap in the middle (between
frames 1-2 and 5-6) suggests the sheet is split into two groups
of 3-4 frames — likely: [intro frames] [gap] [loop frames].

Animation mapping:
  Frames 0-4  → intro + first part of loop
  Frames 5-7  → continuation of loop

You can adjust ANIM_DEFS to slice differently — just change
which frame indices go into each animation slot.

Run from project root:
  .venv\\Scripts\\python tools/generate_spriteframes.py
"""

import sys
from pathlib import Path

# ── Detected frame regions (from detect_rows.py) ──────────────────────────────
# Format: { row_name: [(x, y, w, h), ...] }  — 8 frames per row
DETECTED_FRAMES = {
    "IDLE":     [
        (37, 40, 64, 64), (101, 40, 64, 64), (180, 40, 64, 64), (244, 40, 64, 64),
        (312, 40, 64, 64), (376, 40, 64, 64), (450, 40, 64, 64), (514, 40, 64, 64),
    ],
    "CURIOUS":  [
        (35, 193, 64, 64), (99, 193, 64, 64), (171, 193, 64, 64), (235, 193, 64, 64),
        (304, 193, 64, 64), (368, 193, 64, 64), (452, 193, 64, 64), (516, 193, 64, 64),
    ],
    "FOCUSED":  [
        (27, 356, 64, 64), (91, 356, 64, 64), (161, 356, 64, 64), (225, 356, 64, 64),
        (314, 356, 64, 64), (378, 356, 64, 64), (470, 356, 64, 64), (534, 356, 64, 64),
    ],
    "STRESSED": [
        (33, 501, 64, 64), (97, 501, 64, 64), (161, 501, 64, 64), (225, 501, 64, 64),
        (314, 501, 64, 64), (378, 501, 64, 64), (442, 501, 64, 64), (506, 501, 64, 64),
    ],
    "SLEEPING": [
        (28, 645, 64, 64), (92, 645, 64, 64), (171, 645, 64, 64), (235, 645, 64, 64),
        (321, 645, 64, 64), (385, 645, 64, 64), (473, 645, 64, 64), (537, 645, 64, 64),
    ],
    "HAPPY":    [
        (34, 758, 64, 64), (98, 758, 64, 64), (181, 758, 64, 64), (245, 758, 64, 64),
        (338, 758, 64, 64), (402, 758, 64, 64), (491, 758, 64, 64), (555, 758, 64, 64),
    ],
    "GLITCH":   [
        (25, 888, 64, 64), (89, 888, 64, 64), (179, 888, 64, 64), (243, 888, 64, 64),
        (312, 888, 64, 64), (376, 888, 64, 64), (440, 888, 64, 64), (504, 888, 64, 64),
    ],
}

# ── Animation definitions ──────────────────────────────────────────────────────
# Maps Godot animation name → { "row": sheet row name, "indices": [frame indices], "fps": float, "loop": bool }
#
# ADJUST THESE to match your actual spritesheet content.
# Indices refer to the 0-7 positions in each DETECTED_FRAMES row.
# The gap between frames 1-2 and 5-6 suggests groups:
#   Group A (indices 0-3): 4 frames — likely different poses
#   Group B (indices 4-7): 4 frames — likely continuation/variation
#
# Current mapping: intro = first 2 frames, loop = remaining 6 frames.
# Tweak as needed after inspecting your sheet visually.

ANIM_DEFS = [
    # Idle
    {"name": "idle_loop",       "row": "IDLE",     "indices": list(range(0, 8)), "fps": 5.0,  "loop": True},
    {"name": "blink",           "row": "IDLE",     "indices": [2, 3],            "fps": 14.0, "loop": False},

    # Curious
    {"name": "curious_intro",   "row": "CURIOUS",  "indices": [0, 1],            "fps": 8.0,  "loop": False},
    {"name": "curious_loop",    "row": "CURIOUS",  "indices": list(range(2, 8)), "fps": 6.0,  "loop": True},

    # Focused
    {"name": "focused_intro",   "row": "FOCUSED",  "indices": [0, 1],            "fps": 7.0,  "loop": False},
    {"name": "focused_loop",    "row": "FOCUSED",  "indices": list(range(2, 8)), "fps": 4.0,  "loop": True},

    # Stressed
    {"name": "stressed_intro",  "row": "STRESSED", "indices": [0, 1],            "fps": 10.0, "loop": False},
    {"name": "stressed_loop",   "row": "STRESSED", "indices": list(range(2, 8)), "fps": 8.0,  "loop": True},

    # Sleeping
    {"name": "sleep_intro",     "row": "SLEEPING", "indices": [0, 1, 2],         "fps": 5.0,  "loop": False},
    {"name": "sleep_loop",      "row": "SLEEPING", "indices": list(range(3, 8)), "fps": 3.0,  "loop": True},

    # Happy
    {"name": "happy_intro",     "row": "HAPPY",    "indices": [0, 1],            "fps": 9.0,  "loop": False},
    {"name": "happy_loop",      "row": "HAPPY",    "indices": list(range(2, 8)), "fps": 6.0,  "loop": True},

    # Glitch / corrupted
    {"name": "glitch_loop",     "row": "GLITCH",   "indices": list(range(0, 8)), "fps": 10.0, "loop": True},

    # Lonely — reuses idle frames with slower speed
    {"name": "lonely_loop",     "row": "IDLE",     "indices": [0, 1, 2, 3],      "fps": 3.0,  "loop": True},
]

# ── Paths ──────────────────────────────────────────────────────────────────────
SPRITESHEET_GODOT_PATH = "res://assets/sprites/spritesheet.png"
OUTPUT_PATH = "frontend/assets/sprites/creature_frames.tres"


# ── Generator ──────────────────────────────────────────────────────────────────

def generate():
    # Collect all unique AtlasTexture regions needed
    # Key: (x, y, w, h) → atlas id string
    atlas_map = {}
    counter = [1]

    def get_atlas_id(rect):
        key = rect
        if key not in atlas_map:
            atlas_map[key] = f"Atlas_{counter[0]}"
            counter[0] += 1
        return atlas_map[key]

    # Pre-pass: register all atlas textures
    for anim in ANIM_DEFS:
        row_frames = DETECTED_FRAMES[anim["row"]]
        for idx in anim["indices"]:
            if idx < len(row_frames):
                get_atlas_id(row_frames[idx])

    # Build sub_resource blocks for AtlasTextures
    atlas_blocks = []
    for rect, aid in sorted(atlas_map.items(), key=lambda kv: int(kv[1].split('_')[1])):
        x, y, fw, fh = rect
        atlas_blocks.append(
            f'[sub_resource type="AtlasTexture" id="{aid}"]\n'
            f'atlas = ExtResource("1_sprite")\n'
            f'region = Rect2({x}, {y}, {fw}, {fh})\n'
        )

    # Build animation entries
    anim_entries = []
    for anim in ANIM_DEFS:
        row_frames = DETECTED_FRAMES[anim["row"]]
        frame_refs = []
        for idx in anim["indices"]:
            if idx < len(row_frames):
                aid = get_atlas_id(row_frames[idx])
                frame_refs.append(f'{{"duration": 1.0, "texture": SubResource("{aid}")}}')
        if not frame_refs:
            continue

        loop_str = "true" if anim["loop"] else "false"
        entry = (
            f'{{"frames": [{", ".join(frame_refs)}], '
            f'"loop": {loop_str}, '
            f'"name": &"{anim["name"]}", '
            f'"speed": {anim["fps"]}}}'
        )
        anim_entries.append(entry)

    load_steps = 1 + len(atlas_map) + 1
    output = [
        f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3]\n',
        f'[ext_resource type="Texture2D" path="{SPRITESHEET_GODOT_PATH}" id="1_sprite"]\n',
    ]
    output += atlas_blocks
    output += [
        '[resource]',
        'animations = [\n' + ',\n'.join(anim_entries) + '\n]',
    ]

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_PATH).write_text('\n'.join(output), encoding='utf-8')

    print(f"Generated {len(ANIM_DEFS)} animations, {len(atlas_map)} atlas textures")
    print(f"Output: {OUTPUT_PATH}")
    print()
    print("In Godot:")
    print("  1. Open creature.tscn")
    print("  2. Select Sprite (AnimatedSprite2D)")
    print("  3. Drag creature_frames.tres onto 'Sprite Frames' in Inspector")


if __name__ == "__main__":
    generate()
