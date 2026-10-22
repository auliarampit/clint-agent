#!/usr/bin/env python3
"""Buat ikon menu bar dari ~/.config/clint/avatar.jpg (gambar pribadi, tidak di repo):
ikon.png (diam, avatar polos) dan alir/0..11.png (bilah biru mengalir di bawah avatar saat agent bekerja).
Butuh Pillow."""
import os
from PIL import Image, ImageDraw
CFG = os.path.expanduser("~/.config/clint"); S = 44; A = 32; BIRU = (106, 168, 255, 255)
src = Image.open(os.path.join(CFG, "avatar.jpg")).convert("RGBA")
def bulat(n):
    im = src.resize((n, n), Image.LANCZOS)
    mask = Image.new("L", (n, n), 0); ImageDraw.Draw(mask).ellipse((0, 0, n - 1, n - 1), fill=255)
    return im, mask
im, mask = bulat(S - 4)
diam = Image.new("RGBA", (S, S), (0, 0, 0, 0)); diam.paste(im, (2, 2), mask)
diam.save(os.path.join(CFG, "ikon.png"))
os.makedirs(os.path.join(CFG, "alir"), exist_ok=True)
im, mask = bulat(A)
N, X0, X1, P = 12, 6, S - 6, 12          # bingkai, rel bilah kiri-kanan, panjang potongan biru
for i in range(N):
    f = Image.new("RGBA", (S, S), (0, 0, 0, 0)); f.paste(im, ((S - A) // 2, 0), mask); d = ImageDraw.Draw(f)
    d.rounded_rectangle((X0, S - 6, X1, S - 2), radius=2, fill=(255, 255, 255, 60))
    t = i / (N // 2) if i < N // 2 else 2 - i / (N // 2)       # maju lalu mundur
    x = X0 + t * (X1 - X0 - P)
    d.rounded_rectangle((x, S - 6, x + P, S - 2), radius=2, fill=BIRU)
    f.save(os.path.join(CFG, "alir", f"{i}.png"))
print("ikon dibuat di", CFG)
