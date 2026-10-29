"""Render sample text through the generated .fnt files the way the game's SDF shader does.

Usage: python -I preview.py out.png [scale]
"""
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KO = os.path.join(HERE, "..", "Contents", "mods", "KoreanSdfFont", "42", "media", "fonts", "KO")
SAMPLES = [
    "Fishing 낚시 - 물고기 정보: 잉어 (Carp) 12.5kg",
    "날씨: 좋음 | 바람: 보통 | 온도: 알 수 없음",
    "Hgjy 한글 테스트 ABC 가나다 똠방각하 뷁 ㄱㄴㅎ…",
]


def load(name):
    txt = open(os.path.join(KO, name + ".fnt"), encoding="utf-8").read()
    pages = {int(i): Image.open(os.path.join(KO, f)).convert("RGBA") for i, f in re.findall(r'page id=(\d+) file="([^"]+)"', txt)}
    chars = {}
    for l in txt.splitlines():
        if l.startswith("char "):
            d = {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", l)}
            chars[d["id"]] = d
    lh = int(re.search(r"lineHeight=(\d+)", txt).group(1))
    return pages, chars, lh


def draw(name, text, scale):
    pages, chars, lh = load(name)
    W = sum(chars.get(ord(c), chars[63])["xadvance"] for c in text) + 20
    canvas = np.zeros((lh + 30, W), np.float32)
    x = 10
    for c in text:
        d = chars.get(ord(c), chars[63])
        if d["width"]:
            a = np.asarray(pages[d["page"]])[d["y"]:d["y"] + d["height"], d["x"]:d["x"] + d["width"], 3] / 255.0
            y0, x0 = 15 + d["yoffset"], x + d["xoffset"]
            region = canvas[y0:y0 + a.shape[0], x0:x0 + a.shape[1]]
            np.maximum(region, a[:region.shape[0], :region.shape[1]], out=region)
        x += d["xadvance"]
    img = Image.fromarray((canvas * 255).astype(np.uint8))
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.BILINEAR)
    a = np.asarray(img) / 255.0
    t = 0.25 / scale
    a = np.clip((a - (0.5 - t)) / (2 * t), 0, 1)
    out = np.full(a.shape, 255, np.uint8)
    out = (255 * (1 - a)).astype(np.uint8)
    # baseline guide
    rgb = np.stack([out] * 3, -1)
    by = int((15 + int(re.search(r"base=(\d+)", open(os.path.join(KO, name + ".fnt"), encoding="utf-8").read()).group(1))) * scale)
    rgb[by, :, :] = np.minimum(rgb[by, :, :], [255, 160, 160])
    return Image.fromarray(rgb)


def main():
    out = sys.argv[1]
    scale = float(sys.argv[2]) if len(sys.argv) > 2 else 0.6
    names = [f[:-4] for f in sorted(os.listdir(KO)) if f.endswith(".fnt")]
    rows = []
    for n in names:
        for s in SAMPLES[:2] if n != "sdfRegular" else SAMPLES:
            rows.append(draw(n, s, scale))
    W = max(r.width for r in rows)
    H = sum(r.height for r in rows)
    sheet = Image.new("RGB", (W, H), "white")
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(out)


if __name__ == "__main__":
    main()
