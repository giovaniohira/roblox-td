# Draws the 25 tower portraits (5 families x 5 elements) as 256x256 PNGs.
# Drawn at 1024 and downscaled for antialiasing. Toon style: flat fills + dark outline.
# Usage: python tools/portraits.py <out_dir>. Upload the PNGs to Roblox and paste the
# asset ids into the lobby's ReplicatedStorage.UI (UI.PORTRAITS).
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "portraits")
OUT.mkdir(parents=True, exist_ok=True)
S = 1024
LINE = (42, 26, 18, 255)
W = 14  # outline width

PAL = {  # main, light, dark, accent
    "Fogo": ("#FF6A3D", "#FFB08A", "#B8361A", "#FFD84A"),
    "Agua": ("#3DA5FF", "#A8D8FF", "#1F5FA8", "#E8F6FF"),
    "Vento": ("#4CD98A", "#B4F2CE", "#23885A", "#F4FFB0"),
    "Luz": ("#FFD84A", "#FFF4B8", "#C9971A", "#FFFFFF"),
    "Trevas": ("#8A4DFF", "#C9ADFF", "#4B2399", "#FF5FA2"),
}


def rgb(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def oval(cx, cy, rx, ry, angle=0, n=72):
    a = math.radians(angle)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    return pts


def drop(cx, cy, rx, ry, angle=0, n=72):
    # teardrop, pointed end up before rotation
    a = math.radians(angle)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.sin(t) * math.sin(t / 2), -ry * math.cos(t)
        pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    return pts


def shape(d, pts, fill, outline=True):
    d.polygon(pts, fill=fill, outline=LINE if outline else None, width=W if outline else 0)


def ell(d, cx, cy, rx, ry, fill, outline=True, angle=0):
    shape(d, oval(cx, cy, rx, ry, angle), fill, outline)


def background(main, dark):
    img = Image.new("RGBA", (S, S))
    px = img.load()
    edge = mix(rgb("#140E22"), rgb(dark), 0.35)
    center = mix(rgb("#2A2140"), rgb(main), 0.55)
    for y in range(0, S, 4):
        for x in range(0, S, 4):
            t = min(1, math.hypot(x - S / 2, y - S * 0.55) / (S * 0.62))
            c = mix(center, edge, t ** 1.4)
            for dy in range(4):
                for dx in range(4):
                    px[x + dx, y + dy] = c
    return img


def eyes(d, cx, cy, gap, rx, ry, iris, slant=0):
    for side in (-1, 1):
        x = cx + side * gap
        ell(d, x, cy, rx, ry, (255, 255, 255, 255), angle=side * slant)
        ell(d, x, cy + ry * 0.12, rx * 0.78, ry * 0.8, iris, outline=False, angle=side * slant)
        ell(d, x, cy + ry * 0.18, rx * 0.45, ry * 0.5, (30, 20, 30, 255), outline=False)
        ell(d, x - rx * 0.28, cy - ry * 0.3, rx * 0.26, ry * 0.22, (255, 255, 255, 255), outline=False)
        ell(d, x + rx * 0.25, cy + ry * 0.35, rx * 0.12, ry * 0.1, (255, 255, 255, 230), outline=False)


def blush(d, cx, cy, gap):
    for side in (-1, 1):
        ell(d, cx + side * gap, cy, 48, 26, (255, 120, 150, 150), outline=False)


def smile(d, cx, cy, w=46):
    d.arc((cx - w, cy - w * 0.6, cx + w, cy + w * 0.6), 20, 160, fill=LINE, width=W)


def pixie(d, layer, p):
    main, light, dark, accent = map(rgb, p)
    skin = rgb("#FFE2CC")
    # wings
    wing = rgb(p[3], 170)
    for side in (-1, 1):
        ell(d, 512 + side * 300, 420, 190, 110, wing, angle=side * -35)
        ell(d, 512 + side * 270, 640, 140, 80, wing, angle=side * 30)
    # body + collar
    ell(d, 512, 930, 230, 170, main)
    ell(d, 512, 800, 150, 60, light)
    # back hair
    ell(d, 512, 520, 330, 330, dark)
    # ears
    for side in (-1, 1):
        shape(d, [(512 + side * 250, 560), (512 + side * 390, 470), (512 + side * 255, 650)], skin)
    # face
    ell(d, 512, 590, 265, 245, skin)
    # bangs
    shape(d, oval(512, 400, 300, 170), main)
    for i, x in enumerate((330, 420, 512, 604, 694)):
        ell(d, x, 470 + (i % 2) * 20, 70, 85, main, outline=False)
    d.arc((222, 230, 802, 570), 200, 340, fill=LINE, width=W)
    # side locks
    for side in (-1, 1):
        ell(d, 512 + side * 245, 660, 55, 150, main, angle=side * -8)
    # flower clip
    for k in range(5):
        a = math.radians(72 * k)
        ell(d, 700 + 38 * math.cos(a), 330 + 38 * math.sin(a), 30, 30, accent)
    ell(d, 700, 330, 22, 22, rgb("#FF8FB8"))
    eyes(d, 512, 610, 105, 62, 78, dark)
    blush(d, 512, 700, 150)
    smile(d, 512, 735, 34)


def coruja(d, layer, p):
    main, light, dark, accent = map(rgb, p)
    # tufts
    for side in (-1, 1):
        shape(d, [(512 + side * 150, 330), (512 + side * 330, 170), (512 + side * 290, 400)], dark)
    # wings
    for side in (-1, 1):
        ell(d, 512 + side * 300, 720, 110, 220, dark, angle=side * 15)
    # body
    ell(d, 512, 620, 320, 360, main)
    ell(d, 512, 800, 200, 180, light)
    for row in range(3):
        for col in range(-2 + row % 2, 3, 2):
            d.arc((512 + col * 45 - 30, 730 + row * 55, 512 + col * 45 + 30, 770 + row * 55), 20, 160, fill=dark, width=10)
    # face discs
    for side in (-1, 1):
        ell(d, 512 + side * 125, 520, 135, 135, accent)
    eyes(d, 512, 525, 125, 85, 85, rgb("#FFB020"))
    shape(d, [(472, 615), (552, 615), (512, 690)], rgb("#FF9A2E"))


def dragao(d, layer, p):
    main, light, dark, accent = map(rgb, p)
    cream = rgb("#FFF0D2")
    # wings
    for side in (-1, 1):
        x0 = 512 + side * 240
        shape(d, [(x0, 520), (x0 + side * 200, 260), (x0 + side * 170, 420), (x0 + side * 240, 470), (x0 + side * 140, 560)], dark)
    # body
    ell(d, 512, 930, 250, 170, main)
    ell(d, 512, 950, 140, 110, light)
    # horns
    for side in (-1, 1):
        shape(d, [(512 + side * 120, 360), (512 + side * 250, 160), (512 + side * 215, 390)], cream)
    # head spikes
    for x, y in ((512, 300), (430, 320), (594, 320)):
        shape(d, [(x - 40, y + 40), (x, y - 50), (x + 40, y + 40)], dark)
    # head
    ell(d, 512, 560, 290, 255, main)
    # snout
    ell(d, 512, 700, 175, 105, light)
    for side in (-1, 1):
        ell(d, 512 + side * 55, 680, 16, 12, LINE, outline=False)
    # cheek scales
    for side in (-1, 1):
        for k in range(3):
            ell(d, 512 + side * (215 + k * 18), 560 + k * 40, 20, 14, dark, outline=False)
    eyes(d, 512, 535, 120, 66, 80, accent if p[0] != "#FFD84A" else rgb("#FF8A2E"), slant=-8)
    shape(d, [(560, 745), (590, 745), (575, 785)], (255, 255, 255, 255))
    smile(d, 512, 735, 70)


def tanuki(d, layer, p):
    main, light, dark, accent = map(rgb, p)
    mask = rgb("#3B2A2E")
    # ears
    for side in (-1, 1):
        ell(d, 512 + side * 230, 330, 95, 95, dark)
        ell(d, 512 + side * 230, 340, 50, 50, light, outline=False)
    # body
    ell(d, 512, 940, 260, 170, main)
    ell(d, 512, 960, 150, 120, light)
    # head
    ell(d, 512, 590, 320, 260, main)
    # mask
    for side in (-1, 1):
        ell(d, 512 + side * 130, 590, 110, 85, mask, outline=False, angle=side * 20)
    # muzzle
    ell(d, 512, 700, 150, 100, rgb("#FFF4E4"))
    ell(d, 512, 660, 42, 30, LINE, outline=False)
    smile(d, 512, 720, 40)
    eyes(d, 512, 585, 128, 52, 60, rgb("#8A5A2E"))
    # leaf
    leaf = rgb("#7BCB4A") if p[0] != "#4CD98A" else rgb("#E8E05A")
    shape(d, oval(560, 290, 120, 60, -30), leaf)
    d.line((470, 340, 650, 240), fill=LINE, width=10)
    blush(d, 512, 690, 200)


def kitsune(d, layer, p):
    main, light, dark, accent = map(rgb, p)
    white = rgb("#FFF8F0")
    # teardrop tails rising behind the shoulders, white tips
    for side in (-1, 1):
        a = side * 28
        r = math.radians(a)
        cx, cy = 512 + side * 330, 650
        shape(d, drop(cx, cy, 150, 280, a), main)
        shape(d, drop(cx + math.sin(r) * 175, cy - math.cos(r) * 175, 80, 105, a), white)
    # ears
    for side in (-1, 1):
        shape(d, [(512 + side * 100, 380), (512 + side * 280, 140), (512 + side * 300, 470)], main)
        shape(d, [(512 + side * 150, 390), (512 + side * 270, 220), (512 + side * 270, 430)], light, outline=False)
    # body
    ell(d, 512, 940, 230, 160, main)
    ell(d, 512, 940, 120, 120, white)
    # head
    ell(d, 512, 590, 290, 250, main)
    for side in (-1, 1):
        ell(d, 512 + side * 150, 700, 150, 110, white, outline=False, angle=side * -20)
    ell(d, 512, 735, 130, 70, white, outline=False)
    # markings
    for side in (-1, 1):
        ell(d, 512 + side * 125, 485, 40, 14, accent if p[0] != "#FFD84A" else rgb("#FF4F6A"), outline=False, angle=side * -20)
    eyes(d, 512, 590, 125, 58, 64, dark, slant=12)
    ell(d, 512, 690, 26, 18, LINE, outline=False)
    smile(d, 512, 715, 30)


def sapo(d, layer, p):
    main, light, dark, accent = map(rgb, p)
    belly = rgb("#FFF4DA")
    # legs
    for side in (-1, 1):
        ell(d, 512 + side * 230, 960, 120, 70, dark)
    # body
    ell(d, 512, 900, 270, 170, main)
    ell(d, 512, 930, 170, 120, belly)
    # wide head
    ell(d, 512, 620, 360, 240, main)
    # eye bumps on top
    for side in (-1, 1):
        ell(d, 512 + side * 165, 420, 120, 115, main)
    eyes(d, 512, 425, 165, 72, 80, dark)
    # wide smile and cheeks
    d.arc((312, 560, 712, 760), 25, 155, fill=LINE, width=W)
    blush(d, 512, 680, 230)
    # lily pad hat
    shape(d, oval(512, 300, 150, 50), rgb("#6FCB4A"))
    ell(d, 590, 270, 34, 34, accent)


def golem(d, layer, p):
    main, light, dark, accent = map(rgb, p)
    stone = rgb("#9A93A8")
    stone_dark = rgb("#6E6880")
    # shoulders
    for side in (-1, 1):
        shape(d, [(512 + side * 200, 760), (512 + side * 420, 700), (512 + side * 440, 900), (512 + side * 230, 940)], stone_dark)
    # body
    shape(d, [(290, 780), (734, 780), (780, 1010), (244, 1010)], stone)
    shape(d, [(440, 820), (584, 820), (512, 930)], main)  # chest crystal
    # head (blocky)
    shape(d, [(290, 360), (734, 360), (770, 600), (700, 760), (324, 760), (254, 600)], stone)
    shape(d, [(290, 360), (734, 360), (700, 430), (324, 430)], light)
    # cracks glowing with the element
    d.line((360, 450, 410, 520, 380, 600), fill=main, width=14)
    d.line((660, 470, 620, 540), fill=main, width=14)
    # crystal crown
    for x, h in ((430, 140), (512, 210), (594, 140)):
        shape(d, [(x - 40, 370), (x, 370 - h), (x + 40, 370)], main)
        shape(d, [(x - 15, 360), (x, 370 - h + 40), (x + 5, 360)], light, outline=False)
    eyes(d, 512, 560, 115, 60, 66, dark)
    smile(d, 512, 680, 40)


def fenix(d, layer, p):
    main, light, dark, accent = map(rgb, p)
    # flame wings
    for side in (-1, 1):
        for k, (dx, dy, r) in enumerate(((330, 420, 150), (380, 560, 130), (340, 700, 110))):
            ell(d, 512 + side * dx, dy, r * 1.4, r * 0.55, main if k % 2 == 0 else accent, angle=side * (-30 + k * 25))
    # tail feathers
    for dx in (-90, 0, 90):
        shape(d, drop(512 + dx, 1000, 70, 200, dx / 6), dark)
    # body
    ell(d, 512, 880, 220, 180, main)
    ell(d, 512, 900, 130, 120, light)
    # head
    ell(d, 512, 560, 270, 240, main)
    # crest
    for k, dx in enumerate((-80, 0, 80)):
        shape(d, drop(512 + dx, 330, 50, 190 - abs(dx), dx / 4), accent if k != 1 else light)
    # beak
    shape(d, [(462, 640), (562, 640), (512, 720)], rgb("#FFB020"))
    eyes(d, 512, 560, 115, 62, 74, dark, slant=10)
    blush(d, 512, 650, 175)


def grifo(d, layer, p):
    main, light, dark, accent = map(rgb, p)
    white = rgb("#FFF8F0")
    # big feathered wings
    for side in (-1, 1):
        for k in range(4):
            ell(d, 512 + side * (260 + k * 40), 440 + k * 90, 210 - k * 25, 70, dark if k % 2 else main, angle=side * (-40 + k * 15))
    # lion body
    ell(d, 512, 930, 250, 160, light)
    for side in (-1, 1):
        ell(d, 512 + side * 140, 1000, 70, 50, light)
    # head with feather mane
    for k in range(9):
        a = math.radians(-160 + k * 17.5)
        ell(d, 512 + 270 * math.cos(a), 600 + 250 * math.sin(a), 70, 110, main, angle=math.degrees(a) + 90)
    ell(d, 512, 600, 250, 230, white)
    # ear tufts
    for side in (-1, 1):
        shape(d, [(512 + side * 120, 400), (512 + side * 230, 230), (512 + side * 230, 420)], main)
    # hooked beak
    shape(d, [(440, 650), (584, 650), (560, 720), (512, 770), (476, 720)], accent if p[0] != "#FFD84A" else rgb("#FF9A2E"))
    eyes(d, 512, 580, 110, 60, 70, dark, slant=14)


FAMILIES = {"Pixie": pixie, "Coruja": coruja, "Dragaozinho": dragao, "Tanuki": tanuki, "Kitsune": kitsune,
            "Sapo": sapo, "Golem": golem, "Fenix": fenix, "Grifo": grifo}

if __name__ == "__main__":
    # optional 2nd arg: comma separated families to draw (default: all)
    only = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else set(FAMILIES)
    chosen = [(f, fn) for f, fn in FAMILIES.items() if f in only]
    sheet = Image.new("RGBA", (256 * 5, 256 * len(chosen)))
    for row, (family, draw_fn) in enumerate(chosen):
        for col, (element, pal) in enumerate(PAL.items()):
            img = background(pal[0], pal[2])
            layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            draw_fn(ImageDraw.Draw(layer, "RGBA"), layer, pal)
            img.alpha_composite(layer)
            small = img.resize((256, 256), Image.LANCZOS)
            small.save(OUT / f"{family}_{element}.png")
            sheet.paste(small, (col * 256, row * 256))
    sheet.save(OUT / "_sheet.png")
    print("ok", OUT)
