"""Re-apply shots/crops.json: crop shots/raw/<path> into docs/images/<path>.

Run from anywhere: uv run --with pillow python shots/crop.py
"""
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"

for rel, box in json.loads((HERE / "crops.json").read_text()).items():
    src = HERE / "raw" / Path(rel).relative_to("images")
    dst = DOCS / rel
    with Image.open(src) as im:
        out = im.crop(tuple(box))
        out.save(dst, optimize=True)
    print(f"{rel}: {box} -> {out.size[0]}x{out.size[1]}")
