# assets/sprites/README.md

## Sprite Sheet Requirements

The creature needs a pixel art sprite sheet at:
  `frontend/assets/sprites/creature_sheet.png`

### Style Guide
- Palette: dark navy background (transparent), teal/cyan primary, magenta accent, off-white highlights
- Format: PNG with alpha transparency
- Frame size: 64×64 px recommended
- Look: small alien blob, large expressive eyes, slightly cyberpunk
- No anti-aliasing — crisp pixel art only
- Inspirations: Tamagotchi + Lain + EVA terminal

### Animations Needed
| Animation | Frames | FPS | Description |
|-----------|--------|-----|-------------|
| idle      | 4      | 5   | Gentle breathing cycle |
| blink     | 3      | 12  | Eyes half-close → close → open |
| sleep     | 4      | 2   | Slow rise-fall, eyes closed |
| curious   | 4      | 6   | Head tilt, wide eyes |
| focused   | 4      | 4   | Intense narrow stare, glow |
| stressed  | 4      | 8   | Fidget, slight tremor |
| lonely    | 2      | 3   | Drooped posture, dim |

### Creating Sprites
You can use:
- **Aseprite** (recommended for pixel art animation)
- **LibreSprite** (free Aseprite fork)
- **Pixelorama** (free, open source)
- **GIMP** + manual frame export

Export as a single horizontal strip per animation, or a packed atlas.
Reference the correct frame regions in Godot's `SpriteFrames` editor.

### Placeholder
Until sprites are ready, you can use a simple colored circle.
Create a 64×64 px circle in any image editor and save it at the path above.
The creature will still animate procedurally (breathing, glow, etc.) —
only the sprite artwork will be placeholder.
