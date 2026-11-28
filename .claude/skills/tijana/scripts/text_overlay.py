#!/usr/bin/env python3
"""TikTok-style text overlay (white, soft shadow, centred). usage: text_overlay.py "TEXT" OUT.png [y_center=960] [size=56]"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
txt = sys.argv[1].replace('\\n', '\n'); out = sys.argv[2]
yc = int(sys.argv[3]) if len(sys.argv) > 3 else 960
size = int(sys.argv[4]) if len(sys.argv) > 4 else 56
font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), '../assets/fonts/Montserrat-700.ttf'), size)
W, H = 1080, 1920
lines = txt.split('\n'); lh = int(size * 1.28)
y0 = yc - lh * len(lines) // 2
def draw(col, img):
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        w = d.textlength(l, font=font)
        d.text(((W - w) / 2, y0 + i * lh), l, font=font, fill=col)
sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw((0, 0, 0, 170), sh)
sh = sh.filter(ImageFilter.GaussianBlur(6))
tight = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw((0, 0, 0, 120), tight)
tight = tight.filter(ImageFilter.GaussianBlur(1.5))
img = Image.alpha_composite(sh, tight)
fg = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw((255, 255, 255, 255), fg)
Image.alpha_composite(img, fg).save(out)
