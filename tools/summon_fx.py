"""Textures for the lobby summon cinematic (ReplicatedStorage.SummonFx).

White on transparent so the game tints them by rarity, except the rainbow beam.
Writes into tools/out/summon_fx/: runecircle.png, swirl.png, beam.png, rainbow.png, runes.png.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "out", "summon_fx")
os.makedirs(OUT, exist_ok=True)
random.seed(7)
WHITE = (255, 255, 255, 255)


def glow(img, radius):
    """Adds a blurred copy under the sharp lines."""
    soft = img.filter(ImageFilter.GaussianBlur(radius))
    return Image.alpha_composite(soft, img)


def glyph(d, cx, cy, s, width):
    """One made-up angular rune: a stem plus 2-3 random branches."""
    d.line([(cx, cy - s), (cx, cy + s)], fill=WHITE, width=width)
    for _ in range(random.randint(2, 3)):
        y = cy + random.uniform(-s, s)
        side = random.choice((-1, 1))
        kind = random.random()
        if kind < 0.4:
            d.line([(cx, y), (cx + side * s * 0.7, y - s * 0.5)], fill=WHITE, width=width)
        elif kind < 0.7:
            d.line([(cx, y), (cx + side * s * 0.7, y)], fill=WHITE, width=width)
        else:
            r = s * 0.25
            d.ellipse([cx + side * s * 0.5 - r, y - r, cx + side * s * 0.5 + r, y + r], outline=WHITE, width=width)


def rune_circle(n=1024):
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    for r, w in ((0.48, 10), (0.44, 4), (0.33, 6), (0.30, 3), (0.12, 5)):
        d.ellipse([c - r * n, c - r * n, c + r * n, c + r * n], outline=WHITE, width=w)
    # glyph band between the two outer rings, small glyphs between the middle rings
    for count, rad, size in ((28, 0.46 * n, 0.018 * n), (18, 0.315 * n, 0.012 * n)):
        for i in range(count):
            a = 2 * math.pi * i / count
            gl = Image.new("RGBA", (int(size * 4), int(size * 4)), (0, 0, 0, 0))
            glyph(ImageDraw.Draw(gl), size * 2, size * 2, size, 4)
            gl = gl.rotate(-math.degrees(a) - 90, resample=Image.BICUBIC)
            img.alpha_composite(gl, (int(c + math.cos(a) * rad - gl.width / 2), int(c + math.sin(a) * rad - gl.height / 2)))
    # hexagram in the middle
    for off in (0, math.pi / 3):
        pts = [(c + math.cos(off + k * 2 * math.pi / 3 - math.pi / 2) * 0.30 * n,
                c + math.sin(off + k * 2 * math.pi / 3 - math.pi / 2) * 0.30 * n) for k in range(3)]
        d.polygon(pts, outline=WHITE, width=5)
    return glow(img, 10)


def swirl(n=512):
    """A ring that fades along its length, like a light trail (spins in game)."""
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c, r = n / 2, n * 0.44
    steps = 240
    for i in range(steps):
        t = i / steps
        a0, a1 = 2 * math.pi * t, 2 * math.pi * (t + 1.5 / steps)
        alpha = int(255 * t ** 1.6)
        w = int(4 + 14 * t)
        d.line([(c + math.cos(a0) * r, c + math.sin(a0) * r), (c + math.cos(a1) * r, c + math.sin(a1) * r)],
               fill=(255, 255, 255, alpha), width=w)
    return glow(img, 8)


def beam(w=256, h=256, rainbow=False):
    """Beam texture: x runs along the beam, y across it. Soft edges, faint streaks."""
    img = Image.new("RGBA", (w, h))
    px = img.load()
    streak = [0.75 + 0.25 * math.sin(x / w * 2 * math.pi * 3 + random.random()) for x in range(w)]
    for y in range(h):
        v = abs(y / (h - 1) * 2 - 1)  # 0 center, 1 edge
        a = max(0.0, 1 - v ** 2) ** 1.5
        if rainbow:
            hue = y / h
            r, g, b = (int(255 * (0.55 + 0.45 * math.cos(2 * math.pi * (hue + k / 3)))) for k in (0, 1, 2))
            core = max(0.0, 1 - v * 3)  # white-hot middle
            r, g, b = (int(cc + (255 - cc) * core) for cc in (r, g, b))
        else:
            r = g = b = 255
        for x in range(w):
            px[x, y] = (r, g, b, int(255 * a * streak[x]))
    return img


def rune_sheet(n=512, grid=4):
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cell = n / grid
    for i in range(grid * grid):
        cx, cy = (i % grid + 0.5) * cell, (i // grid + 0.5) * cell
        glyph(d, cx, cy, cell * 0.3, 7)
    return glow(img, 5)


rune_circle().save(os.path.join(OUT, "runecircle.png"))
swirl().save(os.path.join(OUT, "swirl.png"))
beam().save(os.path.join(OUT, "beam.png"))
beam(rainbow=True).save(os.path.join(OUT, "rainbow.png"))
rune_sheet().save(os.path.join(OUT, "runes.png"))
print("ok", OUT)
