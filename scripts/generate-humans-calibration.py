#!/usr/bin/env python3
"""Human scale calibration image — owner's request.

Same art direction, same instruction base, but a SMALLER image whose only subject is human scale:
four humans side by side, one empty tile between each — standing man, standing woman, standing child,
sitting man. Even a heavy human never exceeds one tile in width. This image is the measuring stick for
every future plate: if scale cannot be held here, it cannot be held anywhere."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ANCHOR, ASSETS, PROJECT, STYLE, TARGET, TOOL, human

COMPOSITION = f"""
FRAME AND SCALE — the image is 768 x 384 pixels for a grid of 16 columns by 8 rows. EACH TILE IS
48 x 48 PIXELS AND REPRESENTS ONE METRE. Do NOT draw the grid. Positions are written (column,row),
origin (1,1) top left.

CAMERA — steeply down, about seventy degrees from horizontal, exactly like the plates. Plain ground
fills the frame: short vivid green meadow grass, nothing else. NO horizon, NO sky. Sun from the UPPER
LEFT, one simple soft shadow per figure to the LOWER RIGHT. Bright, frank saturated colours, sharp.

THIS IMAGE HAS ONE SUBJECT: HUMAN SCALE. Take the STYLE from the reference image, NOT its scale.

THE RULES, ABSOLUTE:
- A STANDING adult is EXACTLY 2 TILES TALL: 96 PIXELS from sole to crown. Never more.
- A STANDING child is clearly shorter: about 1.25 tiles, 60 PIXELS.
- A SITTING adult is about 1.25 tiles high, 60 PIXELS — sitting, he is far below standing height.
- NO human exceeds ONE TILE — 48 PIXELS — IN WIDTH, even a heavy, broad or fat one. Every figure fits
  inside a one-tile-wide column.
- Each figure stands on ONE tile of ground, feet together on the tile centre.

FOUR HUMANS, side by side on row 5, ONE EMPTY TILE BETWEEN EACH, all FACING STRAIGHT DOWN towards the
camera, face fully visible, arms relaxed:
1. At (5,5), STANDING man, 2 tiles / 96 pixels tall: {human('HU-001')}
2. At (7,5), STANDING woman, 2 tiles / 96 pixels tall: {human('HU-002')}
3. At (9,5), STANDING child, about 1.25 tiles / 60 pixels tall: {human('HU-013')}
4. At (11,5), SITTING man, seated flat on the grass, about 1.25 tiles / 60 pixels high:
   {human('HU-017')}

Nothing else in the image: no buildings, no creatures, no props, no text, no grid lines.
"""

if __name__ == "__main__":
    # The shared generate() prepends the full-plate frame block (1536 x 1152); this image has its own
    # smaller frame, so the prompt is assembled here without it.
    prompt = f"{STYLE}\n\n{ANCHOR}\n{COMPOSITION}"
    (ASSETS / "prompt-calibration-humains.txt").write_text(prompt, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/calibration-humains.png", prompt], cwd=PROJECT
    ).returncode)
