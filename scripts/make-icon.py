#!/usr/bin/env python3
"""Buat ikon avatar menu bar (~/.config/clint/ikon.png) dari ~/.config/clint/avatar.jpg (gambar pribadi, tidak
di repo). Butuh Pillow. Bilah biru saat agent bekerja digambar aplikasi menubar sendiri."""
import os
from PIL import Image, ImageDraw
CFG = os.path.expanduser("~/.config/clint"); S = 44
im = Image.open(os.path.join(CFG, "avatar.jpg")).convert("RGBA").resize((S, S), Image.LANCZOS)
mask = Image.new("L", (S, S), 0); ImageDraw.Draw(mask).ellipse((0, 0, S - 1, S - 1), fill=255)
ikon = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ikon.paste(im, (0, 0), mask)
ikon.save(os.path.join(CFG, "ikon.png"))
print("ikon dibuat di", CFG)
