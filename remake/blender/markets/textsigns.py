#!/usr/bin/env python3
"""textsigns.py -- the market kit's own small lettered boards (the Grok sign sheets have no plain-text boards):
the logistics tents' signs, the gondola station's, the lot's and the market office's.  Drawn in code (image models
garble text), 256 px cells in 8 columns like the sign atlases, with an L-mode night mask at half resolution:
letters 255 (2.0 HDR at full night, the shared scale), lightbox faces 115 (<= 0.9 HDR), boards 0.

  ~/.venvs/ssc-assets/bin/python remake/blender/markets/textsigns.py
      -> godot_project/remake/markets/kit_text.png, kit_text_emit.png, kit_text.json
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FONTS = os.path.join(ROOT, "reference", "fonts")
OUT = os.path.join(ROOT, "godot_project", "remake", "markets")

# id: (lines, font, board colour, letter colour, edge colour, lit: "letters" | "face" | None, board h px)
BOARDS = {
    "txt_mooring_office": (["MOORING", "OFFICE"], "Bungee-Regular.ttf", "#1f3b6e", "#ffd45a", "#ff7a3c", "letters", 150),
    "txt_weigh_house": (["WEIGH", "HOUSE"], "Bungee-Regular.ttf", "#5a1f6e", "#9ff2ff", "#ffd45a", "letters", 150),
    "txt_crew": (["LINE CREW"], "Bungee-Regular.ttf", "#0f5a4a", "#fff3c8", "#ff5a7a", "letters", 110),
    "txt_first_aid": (["FIRST AID"], "Oswald.ttf", "#f4f1e8", "#c8202a", "#c8202a", "face", 110),
    "txt_gondola": (["GONDOLA", "TO THE ISLAND"], "Righteous-Regular.ttf", "#202a4a", "#fff0b0", "#2bb3b1", "letters", 150),
    "txt_tickets": (["FARES"], "Righteous-Regular.ttf", "#202a4a", "#ffd45a", "#2bb3b1", "letters", 110),
    "txt_entrance": (["ENTRANCE"], "Oswald.ttf", "#1d4d2b", "#f4f1e8", "#f4f1e8", None, 100),
    "txt_exit": (["EXIT"], "Oswald.ttf", "#7a1c1c", "#f4f1e8", "#f4f1e8", None, 100),
    "txt_fire_lane": (["FIRE LANE", "NO PARKING"], "Oswald.ttf", "#f4f1e8", "#c8202a", "#c8202a", None, 140),
    "txt_market_office": (["MARKET", "OFFICE"], "Oswald.ttf", "#22303c", "#f4f1e8", "#c9a23a", "face", 150),
    "txt_vendor_lane": (["VENDORS", "ONLY"], "Oswald.ttf", "#f4f1e8", "#22303c", "#22303c", None, 140),
    "txt_stand_clear": (["STAND CLEAR", "OF THE ROPES"], "Oswald.ttf", "#ffd23a", "#141414", "#141414", None, 140),
    "txt_open": (["OPEN"], "Monoton-Regular.ttf", "#101418", "#ff4a7a", "#2bb3b1", "letters", 110),
    "txt_info": (["INFO"], "Oswald.ttf", "#1f4fa0", "#f4f1e8", "#f4f1e8", "face", 110),
    "txt_lowsky": (["ISLAND", "FAIR"], "Bungee-Regular.ttf", "#101418", "#ffb43a", "#ff4a7a", "letters", 150),
    "txt_cargo": (["CARGO", "HOIST"], "Bungee-Regular.ttf", "#3a3a3a", "#ffd23a", "#ffd23a", "letters", 150),
}


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def draw(lines, font, board, ink, edge, lit, bh, S=3):
    W = 256 * S
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    em = Image.new("L", (W, W), 0)
    d, de = ImageDraw.Draw(im), ImageDraw.Draw(em)
    bh *= S
    y0 = (W - bh) // 2
    box = (6 * S, y0, W - 6 * S, y0 + bh)
    d.rounded_rectangle(box, radius=10 * S, fill=_hex(board) + (255,), outline=_hex(edge) + (255,), width=5 * S)
    if lit == "face":
        de.rounded_rectangle(box, radius=10 * S, fill=115)
    n = len(lines)
    lh = (bh - 22 * S) / n
    for k, t in enumerate(lines):
        size = int(lh * 0.82)
        f = ImageFont.truetype(os.path.join(FONTS, font), size)
        while f.getlength(t) > W - 30 * S and size > 10:
            size -= 2
            f = ImageFont.truetype(os.path.join(FONTS, font), size)
        cy = y0 + 11 * S + lh * (k + 0.5)
        d.text((W / 2, cy), t, font=f, fill=_hex(ink) + (255,), anchor="mm")
        if lit == "letters":
            de.text((W / 2, cy), t, font=f, fill=255, anchor="mm")
        elif lit == "face":
            de.text((W / 2, cy), t, font=f, fill=200, anchor="mm")
    content = [6, (y0 // S), 244, bh // S]
    return im.resize((256, 256), Image.LANCZOS), em.resize((128, 128), Image.LANCZOS), content


def main():
    os.makedirs(OUT, exist_ok=True)
    ids = list(BOARDS)
    cols = 8
    rows = (len(ids) + cols - 1) // cols
    atlas = Image.new("RGBA", (256 * cols, 256 * rows), (0, 0, 0, 0))
    emit = Image.new("L", (128 * cols, 128 * rows), 0)
    out = {}
    for k, cid in enumerate(ids):
        i, j = k % cols, k // cols
        im, em, content = draw(*BOARDS[cid])
        a = im.split()[3].point(lambda v: 255 if v >= 128 else 0)
        im.putalpha(a)
        atlas.paste(im, (256 * i, 256 * j))
        emit.paste(em, (128 * i, 128 * j))
        out[cid] = {"kind": "kit_text", "atlas": "kit_text", "i": i, "j": j, "region": [256 * i, 256 * j, 256, 256],
                    "uv": [i / cols, j / rows, 1 / cols, 1 / rows], "content": content, "text": " / ".join(BOARDS[cid][0]),
                    "lit": BOARDS[cid][5]}
    atlas.save(os.path.join(OUT, "kit_text.png"), optimize=True)
    emit.save(os.path.join(OUT, "kit_text_emit.png"), optimize=True)
    json.dump({"png": "res://remake/markets/kit_text.png", "emit": "res://remake/markets/kit_text_emit.png",
               "size": list(atlas.size), "cells": out}, open(os.path.join(OUT, "kit_text.json"), "w"), indent=1)
    print(len(out), "boards ->", os.path.join(OUT, "kit_text.png"), atlas.size)


if __name__ == "__main__":
    main()
