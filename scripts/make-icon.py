#!/usr/bin/env python3
"""Buat ikon menu bar dari ~/.config/clint/avatar.jpg (gambar pribadi, tidak di repo):
ikon.png (diam) dan putar/0..7.png (cincin berputar saat agent bekerja). Butuh Pillow."""
import os
from PIL import Image, ImageDraw
CFG = os.path.expanduser("~/.config/clint"); S = 44; ORANYE = (240, 149, 74, 255)
src = Image.open(os.path.join(CFG, "avatar.jpg")).convert("RGBA").resize((S - 8, S - 8), Image.LANCZOS)
mask = Image.new("L", (S - 8, S - 8), 0); ImageDraw.Draw(mask).ellipse((0, 0, S - 9, S - 9), fill=255)
def dasar():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); im.paste(src, (4, 4), mask); return im
diam = dasar(); ImageDraw.Draw(diam).ellipse((1, 1, S - 2, S - 2), outline=ORANYE, width=3)
diam.save(os.path.join(CFG, "ikon.png"))
os.makedirs(os.path.join(CFG, "putar"), exist_ok=True)
for i in range(8):
    im = dasar(); d = ImageDraw.Draw(im)
    d.ellipse((1, 1, S - 2, S - 2), outline=(240, 149, 74, 70), width=3)
    a = i * 45 - 90; d.arc((1, 1, S - 2, S - 2), a, a + 110, fill=ORANYE, width=4)
    im.save(os.path.join(CFG, "putar", f"{i}.png"))
print("ikon dibuat di", CFG)
