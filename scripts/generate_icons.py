#!/usr/bin/env python3
"""Build installable app icons using the owner's uploaded pink/purple artwork.

The source is a compact WebP representation of the supplied original image.
It keeps the glowing rounded ring, grid, stars, and blocks, with a restrained
1.5% crop to minimize the empty outside background.
"""
from __future__ import annotations
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "app-icon-source.b64"
OUT = ROOT / "assets"
SIZES = {
    "apple-touch-icon.png": 180,
    "icon-192.png": 192,
    "icon-512.png": 512,
    "favicon-32.png": 32,
}

def main() -> None:
    source = SOURCE.read_text(encoding="ascii")
    icon = Image.open(BytesIO(base64.b64decode(source, validate=False))).convert("RGB")
    if icon.width != icon.height or icon.width < 160:
        raise ValueError("Supplied app icon must be square and at least 160px")
    for filename, size in SIZES.items():
        output = OUT / filename
        icon.resize((size, size), Image.Resampling.LANCZOS).save(output, "PNG", optimize=True)
        with Image.open(output) as check:
            if check.size != (size, size) or check.format != "PNG":
                raise AssertionError(f"Invalid app icon: {filename}")
        print(f"OK {filename}: {size} × {size}")
if __name__ == "__main__":
    main()
