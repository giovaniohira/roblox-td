# Store art for the Creator Hub: game icon, thumbnails, gamepass and crystal pack icons.
# Reuses the spirit drawings from portraits.py (transparent, no portrait background).
# Usage: python tools/store_art.py <out_dir> <battle_screenshot> <lobby_screenshot>
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.argv = [sys.argv[0], *sys.argv[1:]]
OUT = Path(sys.argv[1])
BATTLE, LOBBY = sys.argv[2], sys.argv[3]
sys.argv = [sys.argv[0], str(OUT / "_portraits")]  # portraits.py reads its out dir from argv
import portraits as P  # noqa: E402

OUT.mkdir(parents=True, exist_ok=True)
TITLE = "C:/Windows/Fonts/impact.ttf"
BODY = "C:/Windows/Fonts/segoeuib.ttf"
INK = (40, 24, 12)
GOLD = (255, 214, 90)


def spirit(key, size, fade=False):
    family, element = key.split("_")
    layer = Image.new("RGBA", (P.S, P.S), (0, 0, 0, 0))
    P.FAMILIES[family](ImageDraw.Draw(layer, "RGBA"), layer, P.PAL[element])
    if fade:  # the drawings are cut flat at the bottom edge: fade the last 20% out
        a = layer.split()[3]
        ramp = Image.linear_gradient("L").resize((P.S, P.S)).point(lambda v: 255 if v < 204 else round(255 * (255 - v) / 51))
        layer.putalpha(Image.composite(a, Image.new("L", a.size, 0), ramp))
    return layer.resize((size, size), Image.LANCZOS)


def glow(img, color, radius):
    a = img.split()[3].filter(ImageFilter.GaussianBlur(radius))
    g = Image.new("RGBA", img.size, color + (0,))
    g.putalpha(a.point(lambda v: min(255, v * 2)))
    return g


def paste_spirit(canvas, key, size, cx, cy, halo=(255, 240, 180), fade=True):
    s = spirit(key, size, fade)
    pad = size // 4
    big = Image.new("RGBA", (size + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    big.alpha_composite(s, (pad, pad))
    canvas.alpha_composite(glow(big, halo, size // 14), (cx - size // 2 - pad, cy - size // 2 - pad))
    canvas.alpha_composite(s, (cx - size // 2, cy - size // 2))


def text(d, xy, s, size, fill=(255, 255, 255), font=TITLE, anchor="mm", stroke=None, sw=0):
    f = ImageFont.truetype(font, size)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=stroke or INK)


def radial(size, inner, outer, center=(0.5, 0.5)):
    w, h = size
    img = Image.new("RGB", (w // 4, h // 4))
    px = img.load()
    cx, cy = w // 4 * center[0], h // 4 * center[1]
    rmax = math.hypot(w // 4, h // 4) * 0.6
    for y in range(h // 4):
        for x in range(w // 4):
            t = min(1, math.hypot(x - cx, y - cy) / rmax)
            px[x, y] = tuple(round(inner[i] + (outer[i] - inner[i]) * t) for i in range(3))
    return img.resize(size, Image.BICUBIC).convert("RGBA")


def rays(canvas, cx, cy, color, count=16, alpha=50):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = max(canvas.size) * 1.2
    for i in range(count):
        a0 = 2 * math.pi * i / count
        a1 = a0 + math.pi / count * 0.8
        d.polygon([(cx, cy), (cx + r * math.cos(a0), cy + r * math.sin(a0)), (cx + r * math.cos(a1), cy + r * math.sin(a1))], fill=color + (alpha,))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(6)))


def sparkles(canvas, n, area, seed=1):
    rng = random.Random(seed)
    d = ImageDraw.Draw(canvas)
    x0, y0, x1, y1 = area
    for _ in range(n):
        x, y, r = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(4, 12)
        d.polygon([(x, y - r * 2), (x + r * 0.4, y - r * 0.4), (x + r * 2, y), (x + r * 0.4, y + r * 0.4), (x, y + r * 2), (x - r * 0.4, y + r * 0.4), (x - r * 2, y), (x - r * 0.4, y - r * 0.4)], fill=(255, 250, 220, 230))


def gem(d, cx, cy, r):
    # cut gem: crown + pavilion, light facets
    top = [(cx - r, cy - r * 0.2), (cx - r * 0.55, cy - r * 0.75), (cx + r * 0.55, cy - r * 0.75), (cx + r, cy - r * 0.2)]
    d.polygon(top + [(cx, cy + r)], fill=(70, 170, 255), outline=(20, 50, 110), width=max(2, int(r / 12)))
    d.polygon([(cx - r * 0.55, cy - r * 0.75), (cx + r * 0.55, cy - r * 0.75), (cx + r * 0.3, cy - r * 0.2), (cx - r * 0.3, cy - r * 0.2)], fill=(170, 230, 255))
    d.polygon([(cx - r, cy - r * 0.2), (cx - r * 0.3, cy - r * 0.2), (cx, cy + r)], fill=(110, 200, 255))
    d.polygon([(cx + r, cy - r * 0.2), (cx + r * 0.3, cy - r * 0.2), (cx, cy + r)], fill=(40, 120, 230))
    d.line(top + [(cx, cy + r), top[0]], fill=(20, 50, 110), width=max(2, int(r / 12)), joint="curve")


def rounded_card(size, inner, outer):
    img = radial(size, inner, outer, (0.5, 0.42))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=size[0] // 7, fill=255)
    img.putalpha(mask)
    return img


def save_jpg(img, name, bg=(0, 0, 0)):
    flat = Image.new("RGB", img.size, bg)
    flat.paste(img, mask=img.split()[3])
    flat.save(OUT / name, quality=88)


# ------------------------------------------------------------------ game icon
def game_icon():
    S = 512
    c = radial((S, S), (255, 170, 80), (120, 40, 140), (0.5, 0.45))
    rays(c, S // 2, S * 0.45, (255, 240, 190), 18, 45)
    paste_spirit(c, "Kitsune_Fogo", 400, S // 2, 228, fade=False)
    sparkles(c, 4, (20, 20, 110, 200), seed=3)
    sparkles(c, 4, (400, 20, 490, 200), seed=4)
    d = ImageDraw.Draw(c)
    text(d, (S // 2, 410), "SPIRIT", 92, GOLD, sw=8)
    text(d, (S // 2, 478), "SUMMONERS TD", 54, (255, 255, 255), sw=6)
    c.convert("RGB").save(OUT / "icon.png")


# ----------------------------------------------------------------- thumbnails
def background(path, darken=0.35, blur=2):
    shot = Image.open(path).convert("RGB")
    w, h = shot.size
    cw = min(w, round(h * 16 / 9))
    ch = round(cw * 9 / 16)
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    bg = shot.crop((x0, y0, x0 + cw, y0 + ch)).resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur))
    shade = Image.new("RGB", bg.size, (20, 10, 30))
    return Image.blend(bg, shade, darken).convert("RGBA")


def thumb_battle():
    c = background(BATTLE, 0.4, 3)
    grad = Image.new("RGBA", c.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for x in range(1100):
        gd.line([(x, 0), (x, 1080)], fill=(25, 10, 40, round(200 * (1 - x / 1100))))
    c.alpha_composite(grad)
    d = ImageDraw.Draw(c)
    text(d, (80, 230), "SPIRIT", 210, GOLD, anchor="lm", sw=14)
    text(d, (86, 400), "SUMMONERS TD", 140, (255, 255, 255), anchor="lm", sw=12)
    text(d, (92, 530), "Summon elemental spirits", 58, (255, 240, 210), BODY, "lm", sw=5)
    text(d, (92, 600), "and defend the sanctuary!", 58, (255, 240, 210), BODY, "lm", sw=5)
    for i, (label, color) in enumerate([("FIRE", (255, 106, 61)), ("WATER", (61, 165, 255)), ("WIND", (76, 217, 138)), ("LIGHT", (255, 216, 74)), ("DARK", (138, 77, 255))]):
        x = 92 + i * 170
        d.rounded_rectangle((x, 680, x + 155, 740), radius=30, fill=color + (255,), outline=INK, width=4)
        text(d, (x + 77, 710), label, 32, (255, 255, 255), BODY, sw=3)
    team = [("Dragaozinho_Fogo", 1450, 330, 440), ("Kitsune_Trevas", 1700, 600, 420), ("Pixie_Agua", 1260, 640, 360), ("Coruja_Luz", 1560, 880, 300), ("Tanuki_Vento", 1820, 300, 240)]
    for key, x, y, s in team:
        paste_spirit(c, key, s, x, y)
    sparkles(c, 18, (1100, 60, 1900, 1040), seed=7)
    save_jpg(c, "thumb1.jpg")


def card(key, stars, size):
    family, element = key.split("_")
    main, _, dark, _ = P.PAL[element]
    img = rounded_card((size, round(size * 1.3)), P.rgb(main)[:3], P.rgb(dark)[:3])
    s = spirit(key, round(size * 0.95))
    img.alpha_composite(s, (round(size * 0.025), round(size * 0.22)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, img.width - 1, img.height - 1), radius=size // 7, outline=GOLD, width=max(6, size // 30))
    text(d, (size // 2, round(size * 0.12)), "★" * stars, round(size * 0.13), GOLD, "C:/Windows/Fonts/seguisym.ttf", sw=3)
    return img


def thumb_summon():
    c = background(LOBBY, 0.45, 4)
    rays(c, 960, 620, (255, 220, 120), 22, 60)
    d = ImageDraw.Draw(c)
    text(d, (960, 120), "SUMMON 25 SPIRITS!", 130, GOLD, sw=12)
    cards = [("Pixie_Luz", 4, 300, 330, 640, -10), ("Tanuki_Trevas", 5, 330, 640, 600, -4), ("Kitsune_Fogo", 5, 400, 960, 600, 0), ("Dragaozinho_Luz", 5, 330, 1280, 600, 4), ("Coruja_Agua", 3, 300, 1590, 640, 10)]
    for key, stars, size, cx, cy, angle in cards:
        im = card(key, stars, size).rotate(angle, resample=Image.BICUBIC, expand=True)
        shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
        shadow.putalpha(im.split()[3].point(lambda v: v // 2).filter(ImageFilter.GaussianBlur(14)))
        c.alpha_composite(shadow, (cx - im.width // 2 + 10, cy - im.height // 2 + 16))
        c.alpha_composite(im, (cx - im.width // 2, cy - im.height // 2))
    sparkles(c, 22, (60, 200, 1860, 1040), seed=11)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((560, 950, 1360, 1040), radius=45, fill=(255, 200, 70), outline=INK, width=6)
    text(d, (960, 995), "Free scrolls every day", 52, INK, BODY)
    save_jpg(c, "thumb2.jpg")


def thumb_modes():
    c = background(BATTLE, 0.5, 5)
    d = ImageDraw.Draw(c)
    text(d, (960, 150), "SPIRIT SUMMONERS TD", 120, GOLD, sw=12)
    boxes = [("50", "WAVES"), ("10", "FLOORS"), ("1-4", "PLAYERS")]
    for i, (big, small) in enumerate(boxes):
        x = 360 + i * 600
        d.rounded_rectangle((x - 250, 330, x + 250, 720), radius=60, fill=(40, 24, 50, 220), outline=GOLD, width=8)
        text(d, (x, 480), big, 200, (255, 255, 255), sw=10)
        text(d, (x, 640), small, 70, GOLD, sw=6)
    text(d, (960, 850), "Runes · Evolution · Awakening · Autofarm", 64, (255, 240, 210), BODY, sw=5)
    paste_spirit(c, "Kitsune_Luz", 260, 150, 930)
    paste_spirit(c, "Dragaozinho_Trevas", 260, 1770, 930)
    save_jpg(c, "thumb3.jpg")


# ---------------------------------------------------------- products & passes
def product_icon(name, inner, outer, draw):
    S = 512
    c = rounded_card((S, S), inner, outer)
    rays(c, S // 2, S // 2, (255, 255, 255), 14, 35)
    draw(c, ImageDraw.Draw(c), S)
    flat = Image.new("RGB", (S, S), outer)
    flat.paste(c, mask=c.split()[3])
    flat.save(OUT / name)


def pack(n, gems, label):
    def draw(c, d, S):
        spots = {1: [(256, 220, 130)], 3: [(170, 250, 95), (342, 250, 95), (256, 180, 115)], 5: [(130, 270, 80), (382, 270, 80), (190, 170, 90), (322, 170, 90), (256, 250, 120)]}[gems]
        for x, y, r in spots:
            gem(d, x, y, r)
        sparkles(c, 6, (40, 40, 470, 330), seed=n)
        d = ImageDraw.Draw(c)
        text(d, (256, 440), label, 120, (255, 255, 255), sw=10)
    product_icon(f"pack{n}.png", (150, 110, 255), (50, 20, 110), draw)


def pass_speed(c, d, S):
    for dx in (-70, 70):
        d.polygon([(186 + dx, 120), (316 + dx, 230), (186 + dx, 340)], fill=(255, 255, 255), outline=INK, width=10)
    text(d, (256, 430), "2X", 150, GOLD, sw=12)


def pass_farm(c, d, S):
    moon = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(moon)
    md.ellipse((150, 50, 330, 230), fill=255)
    md.ellipse((205, 30, 375, 200), fill=0)
    c.paste(Image.new("RGBA", (S, S), (255, 236, 150, 255)), mask=moon)
    d = ImageDraw.Draw(c)
    for cx, col in ((190, (255, 106, 61)), (330, (138, 77, 255))):
        pts = [(cx + 75 * math.cos(math.pi / 3 * i + math.pi / 6), 300 + 75 * math.sin(math.pi / 3 * i + math.pi / 6)) for i in range(6)]
        d.polygon(pts, fill=col, outline=INK, width=8)
    text(d, (256, 450), "x2 RUNES", 90, GOLD, sw=9)


def pass_bag(c, d, S):
    d.rounded_rectangle((130, 150, 382, 370), radius=60, fill=(170, 110, 60), outline=INK, width=10)
    d.ellipse((190, 90, 322, 190), outline=INK, width=14)
    d.rectangle((150, 190, 362, 230), fill=(120, 70, 30))
    pts = [(256 + 45 * math.cos(math.pi / 3 * i + math.pi / 6), 290 + 45 * math.sin(math.pi / 3 * i + math.pi / 6)) for i in range(6)]
    d.polygon(pts, fill=(61, 165, 255), outline=INK, width=6)
    text(d, (256, 440), "600", 130, GOLD, sw=11)


if __name__ == "__main__":
    game_icon()
    thumb_battle()
    thumb_summon()
    thumb_modes()
    pack(1, 1, "500")
    pack(2, 3, "1100")
    pack(3, 5, "3000")
    product_icon("pass_speed.png", (255, 170, 70), (170, 60, 20), pass_speed)
    product_icon("pass_farm.png", (120, 90, 220), (30, 20, 80), pass_farm)
    product_icon("pass_bag.png", (110, 210, 120), (30, 100, 50), pass_bag)
    print("ok", OUT)
