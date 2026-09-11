# -*- coding: utf-8 -*-
"""Gera imagem de demo 12x8cm (960x640px) com grid colorido."""
from PIL import Image, ImageDraw, ImageFont

W, H = 960, 640
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 36)

# blocos coloridos
colors = ["#e74c3c","#3498db","#2ecc71","#f1c40f","#9b59b6","#1abc9c"]
cw, ch = 320, 320
x, y = 0, 0
for i, col in enumerate(colors):
    d.rectangle([(x, y), (x + cw, y + ch)], fill=col)
    d.text((x + 10, y + 10), f"Tile {i+1}", font=font, fill="white")
    x += cw
    if x >= W:
        x = 0
        y += ch

d.text((30, H - 60), "DEMO 12x8cm — 3 tiras de ~4.8cm", font=font, fill="black")
img.save(r"C:\Users\Pichau\Desktop\.opencode\projects\sc03-tiling\out\demo_12x8.png")