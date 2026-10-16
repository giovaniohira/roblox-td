# Draws the UI icon atlas: one 1024x1024 PNG, an 8x8 grid of 128 px cells, in the same toon
# style as the portraits (flat fills, highlights, one thick dark outline around the whole
# icon). Each icon is drawn at 512 px and downscaled. NAMES order = cell order, row by row;
# ReplicatedStorage.Icons (both places) has the same list.
# Usage: python tools/icons.py <out_dir>. Upload icons.png and paste the id into Icons.ATLAS.
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "icons")
OUT.mkdir(parents=True, exist_ok=True)
S = 512
CELL = 128
LINE = (42, 26, 18)
INNER = 12  # width of the detail lines inside an icon
FONT = "C:/Windows/Fonts/impact.ttf"


def rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def star_pts(cx, cy, r1, r2, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.radians(rot + 180 * i / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def circle(d, cx, cy, r, fill, line=0):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=LINE if line else None, width=line)


def poly(d, pts, fill, line=0):
    d.polygon(pts, fill=fill, outline=LINE if line else None, width=line)


def rot(pts, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def drop_pts(cx, cy, r, h, n=64):
    # teardrop: circle of radius r at (cx, cy) with its point h above the center
    t = math.degrees(math.acos(r / h))
    a0, a1 = -90 + t, 270 - t
    pts = [(cx, cy - h)]
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def text(d, xy, s, size, fill):
    f = ImageFont.truetype(FONT, size)
    d.text(xy, s, font=f, fill=fill, anchor="mm", stroke_width=10, stroke_fill=LINE)


def sparkle(d, cx, cy, r, fill=(255, 255, 255, 255)):
    poly(d, star_pts(cx, cy, r, r * 0.3, 4, -90), fill)


# ---------------------------------------------------------------------------- icons
# Each takes (d, img) on a transparent 512 canvas; keep shapes inside ~40..472.


def sword(d, img, blade="#E4ECF6", hilt="#FFC83D", grip="#8A5A34", angle=45, length=1.0):
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    g = ImageDraw.Draw(layer)
    top = 256 - 230 * length
    poly(g, [(222, top + 50), (256, top), (290, top + 50), (290, 330), (222, 330)], rgb(blade), INNER)
    poly(g, [(256, top + 10), (256, 322), (226, 322), (226, top + 52)], (255, 255, 255, 255))
    g.line((256, top + 30, 256, 320), fill=LINE, width=6)
    g.rounded_rectangle((160, 322, 352, 368), 18, fill=rgb(hilt), outline=LINE, width=INNER)
    g.rectangle((234, 368, 278, 440), fill=rgb(grip), outline=LINE, width=INNER)
    circle(g, 256, 456, 28, rgb(hilt), INNER)
    img.alpha_composite(layer.rotate(-angle, resample=Image.BICUBIC, center=(256, 256)))


def atk(d, img):
    sword(d, img)


def range_(d, img):
    for r, c in ((200, "#4FC3F7"), (148, "#E8F6FF"), (96, "#4FC3F7"), (44, "#FF5A5A")):
        circle(d, 256, 256, r, rgb(c), INNER)
    d.arc((80, 80, 432, 432), 200, 250, fill=(255, 255, 255, 255), width=18)


def bolt(d, cx=256, cy=256, k=1.0, fill="#FFD84A", light="#FFF4B8"):
    p = [(300, 36), (118, 286), (238, 286), (196, 476), (396, 210), (276, 210), (338, 36)]
    p = [(cx + (x - 256) * k, cy + (y - 256) * k) for x, y in p]
    poly(d, p, rgb(fill), INNER)
    q = [(300, 60), (150, 272), (190, 272), (310, 80)]
    poly(d, [(cx + (x - 256) * k, cy + (y - 256) * k) for x, y in q], rgb(light))


def speed(d, img):
    bolt(d)


def crit(d, img):
    poly(d, star_pts(256, 256, 226, 120, 8, -90), rgb("#FF6A3D"), INNER)
    poly(d, star_pts(256, 256, 120, 64, 8, -67.5), rgb("#FFD84A"))
    circle(d, 256, 256, 36, (255, 255, 255, 255))


def critdmg(d, img):
    poly(d, star_pts(256, 256, 226, 140, 10, -90), rgb("#FF3D7F"), INNER)
    poly(d, star_pts(256, 256, 150, 100, 10, -72), rgb("#FF8AB4"))
    for x in (206, 306):
        d.rounded_rectangle((x - 22, 140, x + 22, 300), 16, fill=(255, 255, 255, 255), outline=LINE, width=10)
        circle(d, x, 350, 26, (255, 255, 255, 255), 10)


def accuracy(d, img):
    circle(d, 256, 256, 196, rgb("#4CD98A"), INNER)
    circle(d, 256, 256, 140, (0, 0, 0, 0))
    d.ellipse((116, 116, 396, 396), outline=LINE, width=INNER)
    for a in range(4):
        p = rot([(240, 40), (272, 40), (272, 170), (240, 170)], 256, 256, 90 * a)
        poly(d, p, rgb("#4CD98A"), INNER)
    circle(d, 256, 256, 34, rgb("#FF5A5A"), INNER)


def skull(d, img, bone="#F4EEE2", eyes="#3A2440", horns=None):
    if horns:
        for side in (-1, 1):
            p = [(256 + side * 100, 150), (256 + side * 210, 40), (256 + side * 200, 120), (256 + side * 150, 200)]
            poly(d, p, rgb(horns), INNER)
    circle(d, 256, 230, 170, rgb(bone), INNER)
    d.rounded_rectangle((176, 330, 336, 446), 30, fill=rgb(bone), outline=LINE, width=INNER)
    circle(d, 256, 230, 158, rgb(bone))
    d.rectangle((188, 320, 324, 400), fill=rgb(bone))
    for x in (194, 318):
        circle(d, x, 240, 48, rgb(eyes), INNER)
        if horns:
            circle(d, x, 244, 18, rgb("#FF4D4D"))
    poly(d, [(256, 300), (232, 340), (280, 340)], rgb(eyes))
    for x in (216, 256, 296):
        d.line((x, 384, x, 446), fill=LINE, width=10)
    d.arc((120, 90, 330, 300), 200, 250, fill=(255, 255, 255, 255), width=18)


def boss(d, img):
    skull(d, img, bone="#E8D8F0", eyes="#2A1430", horns="#E23C4C")


def book(d, img):
    d.rounded_rectangle((96, 70, 416, 450), 26, fill=rgb("#8A4DFF"), outline=LINE, width=INNER)
    d.rectangle((96, 390, 400, 432), fill=rgb("#FFF4DC"), outline=LINE, width=10)
    d.rectangle((96, 70, 150, 450), fill=rgb("#5E2CC8"), outline=LINE, width=10)
    poly(d, star_pts(284, 220, 92, 40), rgb("#FFD84A"), 10)


def skillup(d, img):
    book(d, img)
    arrow(d, img, cx=380, cy=150, k=0.45)


def gold(d, img):
    circle(d, 256, 256, 206, rgb("#E89A1C"), INNER)
    circle(d, 256, 240, 196, rgb("#FFC83D"))
    circle(d, 256, 240, 140, rgb("#FFD96A"), 10)
    poly(d, star_pts(256, 244, 92, 40), rgb("#E8A020"), 10)
    d.arc((90, 74, 360, 344), 200, 250, fill=(255, 255, 255, 255), width=20)


def crystal(d, img):
    outer = [(160, 100), (352, 100), (452, 206), (256, 456), (60, 206)]
    poly(d, outer, rgb("#5AD0FF"), INNER)
    poly(d, [(160, 100), (352, 100), (312, 206), (200, 206)], rgb("#B8EEFF"))
    poly(d, [(352, 100), (452, 206), (312, 206)], rgb("#8EDFFF"))
    poly(d, [(312, 206), (452, 206), (256, 456)], rgb("#2E8FD8"))
    poly(d, [(200, 206), (312, 206), (256, 456)], rgb("#47B8F5"))
    for a, b in (((60, 206), (452, 206)), ((200, 206), (256, 456)), ((312, 206), (256, 456)), ((160, 100), (200, 206)), ((352, 100), (312, 206))):
        d.line((*a, *b), fill=LINE, width=8)
    poly(d, outer, None, INNER)
    sparkle(d, 168, 150, 34)


def mana(d, img):
    circle(d, 256, 256, 200, rgb("#3B4FD8"), INNER)
    circle(d, 236, 236, 160, rgb("#5B7CFF"))
    circle(d, 214, 210, 100, rgb("#8EA6FF"))
    d.arc((96, 96, 416, 416), 30, 120, fill=rgb("#B4C4FF"), width=16)
    sparkle(d, 190, 170, 50)
    sparkle(d, 320, 320, 26)


def scroll(d, img):
    d.rectangle((130, 110, 382, 410), fill=rgb("#FFF0C8"), outline=LINE, width=INNER)
    for y in (180, 230, 280, 330):
        d.line((170, y, 342 - (40 if y == 330 else 0), y), fill=rgb("#B88A4A"), width=14)
    for y in (78, 410):
        d.rounded_rectangle((92, y, 420, y + 56), 28, fill=rgb("#D9A35A"), outline=LINE, width=INNER)
        d.line((112, y + 20, 400, y + 20), fill=rgb("#F2C987"), width=10)
    d.rounded_rectangle((330, 330, 380, 470), 10, fill=rgb("#E23C4C"), outline=LINE, width=10)


def xp(d, img):
    poly(d, star_pts(256, 266, 226, 120), rgb("#4CD98A"), INNER)
    poly(d, star_pts(256, 266, 170, 92), rgb("#7CEFA8"))
    text(d, (256, 286), "XP", 150, (255, 255, 255, 255))


def potion(d, img, liquid="#FF5FA2"):
    circle(d, 256, 316, 150, rgb("#D6F0FF"), INNER)
    d.chord((106, 166, 406, 466), 10, 170, fill=rgb(liquid))
    d.arc((106, 166, 406, 466), 0, 360, fill=LINE, width=INNER)
    d.rectangle((206, 96, 306, 180), fill=rgb("#D6F0FF"), outline=LINE, width=INNER)
    d.rectangle((218, 172, 294, 192), fill=rgb("#D6F0FF"))
    d.rounded_rectangle((190, 44, 322, 108), 14, fill=rgb("#A86A3A"), outline=LINE, width=INNER)
    d.arc((140, 200, 320, 380), 190, 250, fill=(255, 255, 255, 255), width=18)
    circle(d, 300, 380, 18, (255, 255, 255, 180))


def fragment(d, img):
    p = [(250, 40), (360, 150), (330, 300), (390, 360), (270, 470), (150, 380), (190, 250), (130, 170)]
    poly(d, p, rgb("#FF9A3D"), INNER)
    poly(d, [(250, 40), (190, 250), (270, 470), (150, 380), (190, 250), (130, 170)], rgb("#FFC07A"))
    d.line((250, 40, 190, 250, 270, 470), fill=LINE, width=8)
    poly(d, p, None, INNER)
    sparkle(d, 330, 120, 40)


def essence(d, img):
    # drawn white so ImageColor3 can tint it with an element color
    poly(d, drop_pts(256, 310, 150, 290), rgb("#F4F6FF"), INNER)
    circle(d, 256, 320, 96, rgb("#FFFFFF"))
    d.arc((150, 200, 360, 410), 200, 260, fill=rgb("#C9D0E6"), width=18)
    sparkle(d, 256, 320, 60, rgb("#D8DDF0"))


def arcane(d, img):
    p = [(256, 36), (420, 150), (420, 362), (256, 476), (92, 362), (92, 150)]
    poly(d, p, rgb("#B45CFF"), INNER)
    poly(d, [(256, 36), (420, 150), (256, 256), (92, 150)], rgb("#D49CFF"))
    poly(d, [(256, 256), (420, 362), (256, 476)], rgb("#8A34E0"))
    for a, b in (((92, 150), (256, 256)), ((420, 150), (256, 256)), ((256, 256), (256, 476))):
        d.line((*a, *b), fill=LINE, width=8)
    poly(d, p, None, INNER)
    sparkle(d, 256, 160, 54)


def rune(d, img):
    p = [(256 + 210 * math.cos(math.radians(60 * i + 30)), 256 + 210 * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    poly(d, p, rgb("#7E8CB0"), INNER)
    q = [(256 + 150 * math.cos(math.radians(60 * i + 30)), 256 + 150 * math.sin(math.radians(60 * i + 30))) for i in range(6)]
    poly(d, q, rgb("#A7B4D6"), 8)
    d.line((256, 160, 256, 352), fill=rgb("#5FF0FF"), width=26)
    d.line((256, 200, 200, 250, 256, 300, 312, 250, 256, 200), fill=rgb("#5FF0FF"), width=22)


def heart(d, img):
    p = []
    for i in range(100):
        t = 2 * math.pi * i / 100
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        p.append((256 + x * 13, 236 - y * 13))
    poly(d, p, rgb("#FF4D6A"), INNER)
    d.arc((120, 110, 260, 250), 190, 260, fill=rgb("#FFB0BE"), width=22)
    circle(d, 168, 200, 14, (255, 255, 255, 255))


def wave(d, img):
    d.rounded_rectangle((100, 50, 140, 470), 16, fill=rgb("#A86A3A"), outline=LINE, width=INNER)
    p = [(140, 70)]
    for i in range(21):
        x = 140 + 280 * i / 20
        p.append((x, 70 + 18 * math.sin(i / 20 * 2 * math.pi)))
    for i in range(21):
        x = 420 - 280 * i / 20
        p.append((x, 270 + 18 * math.sin((20 - i) / 20 * 2 * math.pi)))
    poly(d, p, rgb("#E23C4C"), INNER)
    poly(d, star_pts(280, 172, 62, 26), rgb("#FFD84A"), 8)
    circle(d, 120, 50, 30, rgb("#FFD84A"), INNER)


def tower(d, img):
    d.rectangle((150, 170, 362, 460), fill=rgb("#B8C0D8"), outline=LINE, width=INNER)
    d.rectangle((120, 120, 392, 190), fill=rgb("#C9D0E6"), outline=LINE, width=INNER)
    for x in (120, 210, 302):
        d.rectangle((x, 62, x + 90, 130), fill=rgb("#C9D0E6"), outline=LINE, width=INNER)
    d.rectangle((150, 190, 200, 460), fill=rgb("#9AA4C2"))
    d.rectangle((150, 170, 362, 460), outline=LINE, width=INNER)
    d.rounded_rectangle((216, 340, 296, 460), 40, fill=rgb("#5A3A2A"), outline=LINE, width=10)
    d.rounded_rectangle((236, 230, 276, 290), 20, fill=rgb("#3A2A4A"), outline=LINE, width=8)


def timer(d, img):
    for y in (52, 420):
        d.rounded_rectangle((110, y, 402, y + 44), 16, fill=rgb("#D9A35A"), outline=LINE, width=INNER)
    p = [(150, 96), (362, 96), (276, 256), (362, 420), (150, 420), (236, 256)]
    poly(d, p, rgb("#E8F6FF"), INNER)
    poly(d, [(190, 140), (322, 140), (262, 230), (250, 230)], rgb("#FFB13D"))
    poly(d, [(256, 300), (340, 410), (172, 410)], rgb("#FFB13D"))
    d.line((256, 236, 256, 410), fill=rgb("#FFB13D"), width=8)


def chest(d, img):
    d.rounded_rectangle((70, 150, 442, 270), 50, fill=rgb("#C9783A"), outline=LINE, width=INNER)
    d.rectangle((70, 230, 442, 440), fill=rgb("#A85E2A"), outline=LINE, width=INNER)
    for x in (130, 360):
        d.rectangle((x, 160, x + 26, 440), fill=rgb("#FFC83D"), outline=LINE, width=8)
    d.rounded_rectangle((216, 230, 296, 330), 14, fill=rgb("#FFC83D"), outline=LINE, width=INNER)
    circle(d, 256, 270, 14, LINE)
    d.arc((90, 165, 300, 330), 200, 250, fill=rgb("#E8A060"), width=16)


def trophy(d, img):
    for side in (-1, 1):
        d.arc((256 + side * 130 - 80, 110, 256 + side * 130 + 80, 270), 0, 360, fill=LINE, width=46)
        d.arc((256 + side * 130 - 80, 110, 256 + side * 130 + 80, 270), 0, 360, fill=rgb("#FFC83D"), width=24)
    d.chord((116, -40, 396, 330), 0, 180, fill=rgb("#FFC83D"), outline=LINE, width=INNER)
    d.rectangle((116, 64, 396, 145), fill=rgb("#FFC83D"))
    d.line((116, 64, 116, 145), fill=LINE, width=INNER)
    d.line((396, 64, 396, 145), fill=LINE, width=INNER)
    d.rounded_rectangle((104, 52, 408, 92), 14, fill=rgb("#FFD96A"), outline=LINE, width=INNER)
    d.rectangle((226, 320, 286, 390), fill=rgb("#E89A1C"), outline=LINE, width=INNER)
    d.rounded_rectangle((150, 384, 362, 460), 16, fill=rgb("#8A5A34"), outline=LINE, width=INNER)
    poly(d, star_pts(256, 190, 66, 28), rgb("#FFF4B8"), 8)


def arrow(d, img, cx=256, cy=256, k=1.0, fill="#6EE86E"):
    p = [(256, 40), (452, 250), (334, 250), (334, 470), (178, 470), (178, 250), (60, 250)]
    p = [(cx + (x - 256) * k, cy + (y - 256) * k) for x, y in p]
    poly(d, p, rgb(fill), INNER)
    q = [(256, 70), (110, 228), (200, 228), (200, 450), (230, 450), (230, 228), (256, 100)]
    poly(d, [(cx + (x - 256) * k, cy + (y - 256) * k) for x, y in q], rgb("#B4F5B4"))


def upgrade(d, img):
    arrow(d, img)


def bag(d, img):
    poly(d, drop_pts(256, 320, 160, 230), rgb("#C98B4A"), INNER)
    circle(d, 256, 320, 150, rgb("#C98B4A"))
    d.ellipse((96, 160, 416, 480), outline=LINE, width=INNER)
    d.rounded_rectangle((176, 120, 336, 160), 18, fill=rgb("#8A5A34"), outline=LINE, width=INNER)
    poly(d, [(200, 120), (150, 50), (256, 90), (362, 50), (312, 120)], rgb("#C98B4A"), INNER)
    circle(d, 256, 330, 82, rgb("#FFC83D"), INNER)
    poly(d, star_pts(256, 334, 50, 22), rgb("#E8A020"))
    d.arc((120, 190, 300, 420), 190, 240, fill=rgb("#E8B07A"), width=16)


def active(d, img):
    circle(d, 256, 256, 210, rgb("#8E44E8"), INNER)
    circle(d, 240, 236, 170, rgb("#A866FF"))
    bolt(d, k=0.72, fill="#FFFFFF", light="#FFF4B8")


def passive(d, img):
    p = [(256, 44), (430, 110), (410, 290), (256, 470), (102, 290), (82, 110)]
    poly(d, p, rgb("#4F8CFF"), INNER)
    poly(d, [(256, 80), (396, 132), (380, 280), (256, 420)], rgb("#2E64D8"))
    poly(d, p, None, INNER)
    poly(d, star_pts(256, 240, 96, 42), rgb("#FFD84A"), 10)


def leader(d, img):
    p = [(70, 400), (70, 150), (170, 260), (256, 110), (342, 260), (442, 150), (442, 400)]
    poly(d, p, rgb("#FFC83D"), INNER)
    d.rectangle((70, 360, 442, 430), fill=rgb("#E89A1C"), outline=LINE, width=INNER)
    for x, y in ((70, 150), (256, 110), (442, 150)):
        circle(d, x, y, 34, rgb("#FFD96A"), INNER)
    for x, c in ((170, "#E23C4C"), (256, "#3DA5FF"), (342, "#4CD98A")):
        circle(d, x, 395, 22, rgb(c), 8)


def fire(d, img):
    p = [(256, 30), (330, 150), (400, 120), (420, 300), (380, 420), (256, 476), (132, 420), (92, 300), (130, 190), (190, 230)]
    poly(d, p, rgb("#FF6A3D"), INNER)
    q = [(256, 200), (310, 290), (340, 260), (350, 360), (310, 430), (256, 450), (202, 430), (166, 360), (200, 300)]
    poly(d, q, rgb("#FFD84A"))
    circle(d, 256, 400, 46, rgb("#FFF4B8"))


def water(d, img):
    poly(d, drop_pts(256, 320, 150, 290), rgb("#3DA5FF"), INNER)
    d.arc((150, 210, 360, 420), 150, 230, fill=rgb("#A8D8FF"), width=24)
    circle(d, 200, 250, 20, (255, 255, 255, 255))


def wind(d, img):
    green, light = rgb("#4CD98A"), rgb("#B4F2CE")
    for y, x1, r, up in ((150, 330, 56, True), (262, 440, 0, None), (370, 300, 46, False)):
        d.line((70, y, x1, y), fill=green, width=44)
        circle(d, 70, y, 22, green)
        circle(d, x1, y, 22, green)
        if up is None:
            continue
        box = (x1 - r, y - 2 * r, x1 + r, y) if up else (x1 - r, y, x1 + r, y + 2 * r)
        d.arc(box, 180, 450, fill=green, width=44) if up else d.arc(box, 270, 540, fill=green, width=44)
    d.line((96, 140, 250, 140), fill=light, width=12)


def light(d, img):
    for i in range(8):
        p = rot([(226, 120), (256, 26), (286, 120)], 256, 256, 45 * i)
        poly(d, p, rgb("#FFB13D"), INNER)
    circle(d, 256, 256, 138, rgb("#FFD84A"), INNER)
    circle(d, 240, 240, 96, rgb("#FFF0A0"))
    sparkle(d, 220, 214, 40)


def dark(d, img):
    circle(d, 256, 256, 200, rgb("#8A4DFF"), INNER)
    circle(d, 340, 196, 170, (0, 0, 0, 0))  # the cut gets the silhouette outline
    d.arc((90, 90, 420, 420), 110, 170, fill=rgb("#C9ADFF"), width=20)
    poly(d, star_pts(392, 330, 58, 24), rgb("#FF5FA2"), 8)


def violent(d, img):
    for i, x in enumerate((150, 256, 362)):
        p = rot([(x - 26, 60), (x + 26, 60), (x + 12, 450), (x - 12, 450)], x, 256, 20)
        poly(d, p, rgb("#E23C4C"), INNER)
        poly(d, rot([(x - 12, 80), (x + 4, 80), (x - 2, 300)], x, 256, 20), rgb("#FF9A9A"))


def rage(d, img):
    p = [(256, 30), (330, 150), (400, 120), (420, 300), (380, 420), (256, 476), (132, 420), (92, 300), (112, 120), (182, 150)]
    poly(d, p, rgb("#E23C4C"), INNER)
    poly(d, [(150, 160), (190, 190), (256, 80), (230, 200), (140, 300)], rgb("#FF8A8A"))
    for side in (-1, 1):  # angry eyes
        e = [(256 + side * 30, 300), (256 + side * 130, 250), (256 + side * 110, 340)]
        poly(d, e, (255, 255, 255, 255), 10)
        circle(d, 256 + side * 88, 306, 18, LINE)


def oval(cx, cy, rx, ry, angle, n=48):
    a = math.radians(angle)
    return [(cx + rx * math.cos(t) * math.cos(a) - ry * math.sin(t) * math.sin(a),
             cy + rx * math.cos(t) * math.sin(a) + ry * math.sin(t) * math.cos(a))
            for t in (2 * math.pi * i / n for i in range(n))]


def swift(d, img):
    bx, by = 120, 400
    for i, angle in enumerate((-82, -60, -38, -16)):
        length = 380 - 50 * i
        a = math.radians(angle)
        cx, cy = bx + length / 2 * math.cos(a), by + length / 2 * math.sin(a)
        poly(d, oval(cx, cy, length / 2, 50, angle), rgb("#E8F6FF" if i % 2 else "#A8D8FF"), INNER)
    circle(d, bx + 20, by - 10, 60, rgb("#3DA5FF"), INNER)


def blade(d, img):
    sword(d, img, blade="#D8C8FF", hilt="#8A4DFF", grip="#3A2440", angle=-45, length=0.8)


def focus(d, img):
    p = []
    for i in range(41):
        t = math.pi * i / 40
        p.append((256 - 220 * math.cos(t), 256 - 150 * math.sin(t) ** 1.2))
    for i in range(41):
        t = math.pi * i / 40
        p.append((256 + 220 * math.cos(t), 256 + 150 * math.sin(t) ** 1.2))
    poly(d, p, rgb("#FFFFFF"), INNER)
    circle(d, 256, 256, 100, rgb("#2EC4B6"), INNER)
    circle(d, 256, 256, 50, rgb("#1A2A3A"))
    circle(d, 226, 222, 20, (255, 255, 255, 255))
    poly(d, p, None, INNER)


def lock(d, img):
    d.arc((136, 50, 376, 300), 180, 360, fill=LINE, width=70)
    d.arc((136, 50, 376, 300), 180, 360, fill=rgb("#B8C0D8"), width=46)
    d.rounded_rectangle((96, 200, 416, 460), 36, fill=rgb("#FFC83D"), outline=LINE, width=INNER)
    circle(d, 256, 300, 34, LINE)
    d.rectangle((242, 300, 270, 390), fill=LINE)


def check(d, img):
    d.line((90, 270, 210, 400, 430, 120), fill=LINE, width=110, joint="curve")
    d.line((90, 270, 210, 400, 430, 120), fill=rgb("#6EE86E"), width=76, joint="curve")
    for x, y in ((90, 270), (430, 120)):
        circle(d, x, y, 38, rgb("#6EE86E"))


def star(d, img):
    poly(d, star_pts(256, 270, 230, 110), rgb("#FFD84A"), INNER)
    poly(d, star_pts(256, 270, 150, 72), rgb("#FFF0A0"))


def fast(d, img):
    for x in (60, 250):
        poly(d, [(x, 100), (x + 200, 256), (x, 412)], rgb("#FFFFFF"), INNER)
        poly(d, [(x + 24, 150), (x + 140, 250), (x + 24, 250)], rgb("#C9D0E6"))


def players(d, img):
    for cx, c in ((330, "#8EA6FF"), (190, "#FFD84A")):
        circle(d, cx, 170, 80, rgb(c), INNER)
        d.chord((cx - 140, 270, cx + 140, 560), 180, 360, fill=rgb(c), outline=LINE, width=INNER)


def chevron(d, img):  # small "next / more" arrow
    d.line((180, 90, 350, 256, 180, 422), fill=LINE, width=120, joint="curve")
    d.line((180, 90, 350, 256, 180, 422), fill=rgb("#FFFFFF"), width=80, joint="curve")


def diamond(d, img):  # title ornament
    poly(d, [(256, 30), (446, 256), (256, 482), (66, 256)], rgb("#E8A020"), INNER)
    poly(d, [(256, 100), (376, 256), (256, 412), (136, 256)], rgb("#FFD96A"))
    poly(d, [(256, 100), (376, 256), (256, 256)], rgb("#FFF0A0"))


def close(d, img):
    for a, b in (((120, 120), (392, 392)), ((392, 120), (120, 392))):
        d.line((*a, *b), fill=rgb("#F4F0E8"), width=104)
        for x, y in (a, b):
            circle(d, x, y, 52, rgb("#F4F0E8"))
    d.line((150, 150, 230, 230), fill=(255, 255, 255, 255), width=30)


def glow(d, img):  # soft radial light, white so ImageColor3 tints it; drawn without outline
    px = img.load()
    for y in range(S):
        for x in range(S):
            t = math.hypot(x - 256, y - 256) / 250
            if t < 1:
                px[x, y] = (255, 255, 255, round(255 * (1 - t) ** 2))


ROCK = [(150, 70), (330, 50), (440, 170), (450, 330), (360, 460), (170, 470), (70, 360), (60, 180)]


def carved_rock(d, base, light, dark):
    poly(d, ROCK, rgb(base), INNER)
    poly(d, [(150, 70), (330, 50), (440, 170), (300, 160), (180, 190), (60, 180)], rgb(light))
    poly(d, [(450, 330), (360, 460), (170, 470), (260, 400), (380, 330)], rgb(dark))


def glyph(d, socket, glow, core=(255, 255, 255, 255)):
    poly(d, ROCK, None, INNER)
    circle(d, 256, 280, 110, rgb(socket), 10)
    poly(d, star_pts(256, 286, 92, 40), rgb(glow))
    poly(d, star_pts(256, 286, 50, 22), core)
    sparkle(d, 380, 110, 40)
    sparkle(d, 120, 380, 26)


def stone(d, img):  # Summon Stone: carved violet rock with a glowing star glyph
    carved_rock(d, "#6E5FA6", "#9C8CD8", "#4E4088")
    glyph(d, "#2A1F5A", "#7FF5FF")


def stone_legend(d, img):  # Legendary Stone: gold rock, fiery glyph
    carved_rock(d, "#E0962A", "#FFD36A", "#A8601A")
    glyph(d, "#5A2A08", "#FF6A3D", rgb("#FFF4B8"))


def stone_ld(d, img):  # Light & Dark Stone: white left half, black right half
    carved_rock(d, "#F2EEFA", "#FFFFFF", "#C9C0DE")
    dark = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dark)
    carved_rock(dd, "#3A2A5E", "#5A4690", "#22183E")
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).polygon([(270, 0), (512, 0), (512, 512), (230, 512)], fill=255)
    img.paste(dark, (0, 0), Image.composite(dark.split()[3], Image.new("L", (S, S), 0), mask))
    glyph(d, "#14102A", "#FFD84A")
    poly(d, star_pts(256, 286, 92, 40), None, 8)


def stone_trans(d, img):  # Transcendence Stone: pink crystal rock, rainbow glow
    carved_rock(d, "#D94FB8", "#FF9AE6", "#962A80")
    glyph(d, "#3A0E34", "#FFE15A")
    circle(d, 256, 280, 128, None, 0)
    d.arc((136, 160, 376, 400), 200, 340, fill=rgb("#7FF5FF"), width=12)


def hex_(d, img):  # blank rune stone; the set glyph goes on top in the UI
    outer = [(256 + 220 * math.cos(math.radians(60 * i - 90)), 256 + 220 * math.sin(math.radians(60 * i - 90))) for i in range(6)]
    inner = [(256 + 168 * math.cos(math.radians(60 * i - 90)), 256 + 168 * math.sin(math.radians(60 * i - 90))) for i in range(6)]
    poly(d, outer, rgb("#8C8378"), INNER)
    poly(d, [outer[5], outer[0], inner[0], inner[5]], rgb("#C9C0B4"))
    poly(d, [outer[4], outer[5], inner[5], inner[4]], rgb("#B3AA9E"))
    poly(d, [outer[2], outer[3], inner[3], inner[2]], rgb("#6E665C"))
    poly(d, inner, rgb("#A39A8E"), 8)
    poly(d, outer, None, INNER)


NO_OUTLINE = {"glow"}

ICONS = [
    ("atk", atk), ("range", range_), ("speed", speed), ("crit", crit),
    ("critdmg", critdmg), ("accuracy", accuracy), ("boss", boss), ("skillup", skillup),
    ("gold", gold), ("crystal", crystal), ("mana", mana), ("scroll", scroll),
    ("xp", xp), ("potion", potion), ("fragment", fragment), ("essence", essence),
    ("arcane", arcane), ("rune", rune), ("heart", heart), ("wave", wave),
    ("tower", tower), ("timer", timer), ("skull", skull), ("chest", chest),
    ("trophy", trophy), ("upgrade", upgrade), ("bag", bag), ("active", active),
    ("passive", passive), ("leader", leader), ("fire", fire), ("water", water),
    ("wind", wind), ("light", light), ("dark", dark), ("violent", violent),
    ("rage", rage), ("swift", swift), ("blade", blade), ("focus", focus),
    ("lock", lock), ("check", check), ("star", star), ("fast", fast),
    ("players", players), ("chevron", chevron), ("book", book), ("diamond", diamond),
    ("close", close), ("glow", glow), ("stone", stone), ("hex", hex_), ("stone_legend", stone_legend),
    ("stone_ld", stone_ld), ("stone_trans", stone_trans),
]


def render(name, fn):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    fn(ImageDraw.Draw(img), img)
    if name in NO_OUTLINE:
        return img.resize((CELL - 8, CELL - 8), Image.LANCZOS)
    # one outline around the whole silhouette, then a soft drop shadow under it
    a = img.split()[3].filter(ImageFilter.GaussianBlur(7)).point(lambda v: 255 if v > 24 else 0)
    out = Image.new("RGBA", (S, S), LINE + (0,))
    out.putalpha(a)
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shadow.paste(Image.new("RGBA", (S, S), (10, 6, 30, 110)), (0, 12), a.filter(ImageFilter.GaussianBlur(4)))
    res = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    res.alpha_composite(shadow)
    res.alpha_composite(out)
    res.alpha_composite(img)
    return res.resize((CELL - 8, CELL - 8), Image.LANCZOS)


if __name__ == "__main__":
    assert len(ICONS) <= 64 and len({n for n, _ in ICONS}) == len(ICONS)
    atlas = Image.new("RGBA", (CELL * 8, CELL * 8), (0, 0, 0, 0))
    for i, (name, fn) in enumerate(ICONS):
        atlas.alpha_composite(render(name, fn), (i % 8 * CELL + 4, i // 8 * CELL + 4))
    atlas.save(OUT / "icons.png")
    # preview on the panel color, 2x, with names
    prev = Image.new("RGBA", (CELL * 8, CELL * 8), (52, 58, 128, 255))
    prev.alpha_composite(atlas)
    pd = ImageDraw.Draw(prev)
    for i, (name, _) in enumerate(ICONS):
        pd.text((i % 8 * CELL + 4, i // 8 * CELL + 112), name, fill=(255, 255, 255, 255))
    prev.save(OUT / "preview.png")
    print("names:", ", ".join(f'"{n}"' for n, _ in ICONS))
