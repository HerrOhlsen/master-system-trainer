"""Generate the app icons: a grid of one hundred cells, one lit up.

The icon says what the app is about at a glance: one hundred numbers, and the
slow work of lighting them up one by one.
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
INK = (18, 22, 31)
DIM = (32, 40, 55)
BRASS = (217, 164, 65)
MID = (120, 96, 48)

# Which cells are lit, as a share of the 10x10 grid, arranged so the icon reads
# as progress rather than as a random pattern.
LIT = {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9),
       (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
       (2, 0), (2, 1), (2, 2)}
HALF = {(1, 7), (1, 8), (2, 3), (2, 4), (2, 5), (3, 0), (3, 1)}


def build(size, path):
    scale = 4
    canvas = size * scale
    image = Image.new("RGB", (canvas, canvas), INK)
    draw = ImageDraw.Draw(image)

    margin = canvas * 0.16
    span = canvas - 2 * margin
    step = span / 10
    cell = step * 0.72
    radius = max(2, int(cell * 0.22))

    for row in range(10):
        for column in range(10):
            x = margin + column * step
            y = margin + row * step
            if (row, column) in LIT:
                color = BRASS
            elif (row, column) in HALF:
                color = MID
            else:
                color = DIM
            draw.rounded_rectangle([x, y, x + cell, y + cell], radius=radius, fill=color)

    image = image.resize((size, size), Image.LANCZOS)
    image.save(path)
    print("Geschrieben:", path.name)


if __name__ == "__main__":
    build(192, ROOT / "icon-192.png")
    build(512, ROOT / "icon-512.png")
    build(180, ROOT / "icon-180.png")
