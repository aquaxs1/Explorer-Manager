"""
Render the website logo (site/assets/mark.svg) into the raster formats the
desktop app needs: a Windows .ico for the window/taskbar/exe icon and a PNG
for the header of the GUI.

Run from the repository root:

    pip install pillow cairosvg
    python tools/make_icons.py
"""

from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "site" / "assets" / "mark.svg"
ASSETS = ROOT / "assets"

ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)
HEADER_HEIGHT = 96  # rendered large, the GUI scales it down


def render(width: int) -> Image.Image:
    """Rasterise mark.svg at the given width, preserving its aspect ratio."""
    png = cairosvg.svg2png(url=str(SOURCE), output_width=width)
    return Image.open(BytesIO(png)).convert("RGBA")


def squared(size: int) -> Image.Image:
    """The mark centred on a transparent square canvas (icons must be square)."""
    mark = render(size)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(mark, (0, (size - mark.height) // 2), mark)
    return canvas


def main() -> None:
    ASSETS.mkdir(exist_ok=True)

    largest = squared(max(ICO_SIZES))
    largest.save(ASSETS / "icon.ico", format="ICO",
                 sizes=[(s, s) for s in ICO_SIZES])
    largest.save(ASSETS / "icon.png", format="PNG")

    header = render(round(HEADER_HEIGHT * 128 / 116))
    header.save(ASSETS / "logo.png", format="PNG")

    print(f"Wrote {ASSETS/'icon.ico'}, {ASSETS/'icon.png'} and {ASSETS/'logo.png'}")


if __name__ == "__main__":
    main()
