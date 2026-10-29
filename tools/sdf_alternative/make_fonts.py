"""Build Korean SDF fonts for Project Zomboid B42.

Vanilla SDF fonts (sdfRegular.fnt etc.) have no Hangul, so the new PZAPI UI
(fishing window, build menu, print media) draws Korean text as '?'. The game
looks up media/fonts/<lang>/<file> before media/fonts/<file> (TextManager.
getFontFilePath), so a mod can ship media/fonts/KO/sdfRegular.fnt. Each output
.fnt keeps every vanilla glyph and page (Latin looks unchanged) and adds Hangul
glyphs on extra pages. Upright and italic fonts share the same Hangul pages.

Usage: python -I make_fonts.py [game_dir]
"""
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "Contents", "mods", "KoreanSdfFont", "42")
OUT = os.path.join(MOD, "media", "fonts", "KO")
GAME = sys.argv[1] if len(sys.argv) > 1 else r"C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid"
VFONTS = os.path.join(GAME, "media", "fonts")
VTRANS = os.path.join(GAME, "media", "lua", "shared", "Translate", "KO")
TTF_DIRS = [os.path.join(HERE, "ttf"), os.path.expanduser(r"~/AppData/Local/Microsoft/Windows/Fonts"), r"C:/Windows/Fonts"]

UPSCALE = 8      # render at 8x, then box-filter down
PAGE = 2048      # Hangul page size

# Korean atlas -> TTF. Each vanilla font below names the atlas it borrows Hangul from.
ATLASES = {
    "KoGothic": "NanumGothic.ttf",
    "KoGothicBold": "NanumGothicBold.ttf",
    "KoMyeongjo": "NanumMyeongjo.ttf",
    "KoMyeongjoBold": "NanumMyeongjoBold.ttf",
    "KoGothicHeavy": "NanumGothicExtraBold.ttf",
    "KoPen": "NanumPen.ttf",
}
FONTS = {
    "sdfRegular": "KoGothic",
    "sdfItalic": "KoGothic",
    "sdfBold": "KoGothicBold",
    "sdfBoldItalic": "KoGothicBold",
    "SdfOldRegular": "KoMyeongjo",
    "SdfOldItalic": "KoMyeongjo",
    "SdfOldBold": "KoMyeongjoBold",
    "SdfOldBoldItalic": "KoMyeongjoBold",
    "sdfRobertoSans": "KoGothicHeavy",
    "sdfCaveat": "KoPen",
}


def find_ttf(name):
    for d in TTF_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    sys.exit("missing font " + name)


def parse_fnt(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    info = lines[0]
    common = lines[1]
    pages = [re.search(r'file="([^"]+)"', l).group(1) for l in lines if l.startswith("page ")]
    chars = {}
    for l in lines:
        if l.startswith("char "):
            d = dict(re.findall(r"(\w+)=(-?\d+)", l))
            chars[int(d["id"])] = {k: int(v) for k, v in d.items()}
    kern = [l for l in lines if l.startswith("kerning ")]
    head = dict(re.findall(r"(\w+)=(-?\d+)", info + " " + common))
    pad = int(re.search(r"padding=(\d+)", info).group(1))
    return {"info": info, "common": common, "pages": pages, "chars": chars, "kern": kern,
            "size": int(head["size"]), "base": int(head["base"]), "pad": pad}


def charset(exclude):
    """KS X 1001 Hangul (2350) + every char the vanilla KO translation uses + jamo."""
    cs = set()
    for a in range(0xB0, 0xC9):
        for b in range(0xA1, 0xFF):
            cs.add(bytes([a, b]).decode("euc-kr"))
    cs |= {chr(c) for c in range(0x3131, 0x318F)}
    for dp, _, fs in os.walk(VTRANS):
        for f in fs:
            cs |= set(open(os.path.join(dp, f), encoding="utf-8", errors="ignore").read())
    return sorted(c for c in cs if ord(c) > 32 and ord(c) not in exclude and ord(c) <= 0xFFFF
                  and not (0xD800 <= ord(c) <= 0xDFFF) and c.isprintable())


def ink_height(font, ch):
    l, t, r, b = font.getbbox(ch, anchor="ls")
    return b - t


def render_glyph(font, ch, pad, base):
    """Return (alpha array, xoffset, yoffset, xadvance) in output pixels."""
    U = UPSCALE
    l, t, r, b = font.getbbox(ch, anchor="ls")
    if r <= l or b <= t:
        return None
    ol, ot = l // U, t // U
    orr, ob = -(-r // U), -(-b // U)
    w, h = orr - ol + 2 * pad, ob - ot + 2 * pad
    img = Image.new("L", (w * U, h * U), 0)
    ImageDraw.Draw(img).text(((pad - ol) * U, (pad - ot) * U), ch, font=font, fill=255, anchor="ls")
    m = np.asarray(img) >= 128
    sd = distance_transform_edt(m) - distance_transform_edt(~m)
    sd = sd.reshape(h, U, w, U).mean(axis=(1, 3)) / U
    a = np.clip(0.5 + sd / (2.0 * pad), 0.0, 1.0)
    return (a * 255 + 0.5).astype(np.uint8), ol - pad, base + ot - pad


def build_atlas(name, ttf, ref, chars):
    """ref: parsed vanilla fnt whose size/pad/base/cap height this atlas matches."""
    U = UPSCALE
    # Size Hangul by its own height, not the TTF's Latin: NanumPen's Latin is tiny next to its Hangul.
    # Target: Hangul as tall relative to the vanilla cap height as in NanumGothic.
    cap = ref["chars"][ord("H")]["height"] - 2 * ref["pad"]
    gothic = ImageFont.truetype(find_ttf(ATLASES["KoGothic"]), 100 * U)
    target = cap * ink_height(gothic, "한") / ink_height(gothic, "H")
    probe = ImageFont.truetype(ttf, 100 * U)
    px = 100.0 * target / (ink_height(probe, "한") / U)
    font = ImageFont.truetype(ttf, round(px * U))
    glyphs = []
    for ch in chars:
        if font.getmask(ch).getbbox() is None and ch.strip():
            continue  # TTF lacks this char
        g = render_glyph(font, ch, ref["pad"], ref["base"])
        adv = round(font.getlength(ch) / U)
        if g is None:
            glyphs.append((ch, None, 0, 0, adv))
        else:
            glyphs.append((ch,) + g + (adv,))
    # shelf packing, tallest first
    order = sorted(range(len(glyphs)), key=lambda i: -(glyphs[i][1].shape[0] if glyphs[i][1] is not None else 0))
    pages, placed = [], {}
    x = y = shelf = 0
    cur = None
    for i in order:
        ch, a, xo, yo, adv = glyphs[i]
        if a is None:
            placed[ch] = (0, 0, 0, 0, xo, yo, adv, 0)
            continue
        h, w = a.shape
        if cur is None or x + w > PAGE:
            x, y, shelf = 0, y + shelf, 0
        if cur is None or y + h > PAGE:
            cur = np.zeros((PAGE, PAGE), np.uint8)
            pages.append(cur)
            x = y = shelf = 0
        cur[y:y + h, x:x + w] = a
        placed[ch] = (x, y, w, h, xo, yo, adv, len(pages) - 1)
        x += w
        shelf = max(shelf, h)
    files = []
    for n, p in enumerate(pages):
        used = int(np.nonzero(p.any(axis=1))[0].max()) + 1
        hgt = 1 << (used - 1).bit_length()  # trim the last page to a power of two
        rgba = np.zeros((hgt, PAGE, 4), np.uint8)
        rgba[..., :3] = 255
        rgba[..., 3] = p[:hgt]
        f = "%s%d.png" % (name, n + 1)
        Image.fromarray(rgba, "RGBA").save(os.path.join(OUT, f), optimize=True)
        files.append(f)
    print("[KoreanSdfFont] %s: %d glyphs, %d pages, %.1fpx" % (name, len(placed), len(files), px))
    return files, placed


def write_fnt(vname, v, kfiles, kplaced):
    base_pages = len(v["pages"])
    pages = v["pages"] + kfiles
    info = v["info"]
    common = re.sub(r"pages=\d+", "pages=%d" % len(pages), v["common"])
    out = [info, common]
    out += ['page id=%d file="%s"' % (i, f) for i, f in enumerate(pages)]
    rows = []
    for cid in sorted(v["chars"]):
        c = v["chars"][cid]
        rows.append((cid, c["x"], c["y"], c["width"], c["height"], c["xoffset"], c["yoffset"], c["xadvance"], c["page"]))
    for ch, (x, y, w, h, xo, yo, adv, pg) in sorted(kplaced.items()):
        if ord(ch) in v["chars"]:
            continue
        rows.append((ord(ch), x, y, w, h, xo, yo, adv, base_pages + pg))
    out.append("chars count=%d" % len(rows))
    for r in rows:
        out.append("char id=%-6d x=%-5d y=%-5d width=%-4d height=%-4d xoffset=%-4d yoffset=%-4d xadvance=%-4d page=%-4d chnl=0 " % r)
    out.append("kernings count=%d" % len(v["kern"]))
    out += v["kern"]
    with open(os.path.join(OUT, vname + ".fnt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    for p in v["pages"]:
        shutil.copyfile(os.path.join(VFONTS, p), os.path.join(OUT, p))


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    vanilla = {n: parse_fnt(os.path.join(VFONTS, n + ".fnt")) for n in FONTS}
    atlases = {}
    for an, ttf in ATLASES.items():
        users = [n for n, a in FONTS.items() if a == an]
        ref = vanilla[users[0]]
        for u in users[1:]:
            if (vanilla[u]["size"], vanilla[u]["pad"], vanilla[u]["base"]) != (ref["size"], ref["pad"], ref["base"]):
                sys.exit("%s and %s cannot share %s" % (users[0], u, an))
        atlases[an] = build_atlas(an, find_ttf(ttf), ref, charset(set(ref["chars"])))
    for n, an in FONTS.items():
        write_fnt(n, vanilla[n], *atlases[an])


if __name__ == "__main__":
    main()
