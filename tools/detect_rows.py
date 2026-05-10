"""
Precise frame boundary finder.
Scans each animation row, finds every column where a 'frame cluster'
of content starts, and outputs exact (x, y, w, h) regions per frame.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image

img = Image.open('assets/sprites/spritesheet.png').convert('RGBA')
w, h = img.size
px = img.load()

print(f"Sheet: {w}x{h}")
print()

animation_bands = [
    ('IDLE',     20,  150),
    ('CURIOUS',  173, 299),
    ('FOCUSED',  336, 436),
    ('STRESSED', 481, 587),
    ('SLEEPING', 625, 710),
    ('HAPPY',    738, 845),
    ('GLITCH',   868, 967),
]

FRAME_W = 64
FRAME_H = 64
MAX_FRAMES = 8
LEFT_PANEL_WIDTH = w // 2  # only scan left half

def col_has_pixels(x, y_top, y_bot, threshold=30, min_alpha=20):
    """Does this column have any visible pixels between y_top and y_bot?"""
    for y in range(y_top, min(y_bot, h)):
        r, g, b, a = px[x, y]
        if a > min_alpha and (r > threshold or g > threshold or b > threshold):
            return True
    return False

for name, y0, y1 in animation_bands:
    # Find the actual content Y range within the band (skip label text at top)
    # Labels tend to be thin horizontal text — content frames are tall
    content_y0 = y0
    for y in range(y0, y1):
        if any(px[x, y][3] > 40 and (px[x, y][0] > 50 or px[x, y][1] > 50 or px[x, y][2] > 50)
               for x in range(0, min(LEFT_PANEL_WIDTH, 700), 8)):
            # Found first content row — but check if it's label (thin) or frame (tall)
            # A label row will have very few content rows. Skip first 20px of band.
            content_y0 = max(y, y0 + 20)
            break

    # Now scan columns left→right to find frame clusters
    frames = []
    x = 0
    while x < LEFT_PANEL_WIDTH and len(frames) < MAX_FRAMES:
        if col_has_pixels(x, content_y0, min(content_y0 + FRAME_H, y1)):
            # Found start of a frame cluster — snap to FRAME_W grid
            frame_x = x
            frames.append(frame_x)
            x += FRAME_W  # skip to next expected frame position
        else:
            x += 1

    # Output
    print(f"=== {name} ===")
    print(f"  content_y = {content_y0}  (band: {y0}..{y1})")
    for i, fx in enumerate(frames):
        print(f"  frame {i}: Rect2({fx}, {content_y0}, {FRAME_W}, {FRAME_H})")
    print(f"  total frames detected: {len(frames)}")
    print()
