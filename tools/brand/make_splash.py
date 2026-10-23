"""Compose the boot splash: Grok's travel-poster art + Grok's SVG logo (rendered with our fonts).

usage: python tools/brand/make_splash.py ART.jpg OUT.png
  art in use: reference/grok/splash/r4_img3.jpg (gitignored; briefs in tools/brand/splash_brief*.md)
  logo: tools/brand/columbia_logo.svg (Grok, brief tools/brand/logo_brief.md); also rendered to
        godot_project/ui/brand/columbia_logo.png
  OUT = godot_project/ui/pda/splash.png
The logo's <text> uses Limelight and Lobster (OFL, reference/fonts); rsvg-convert finds them through a
throwaway fontconfig file, since Godot's SVG importer can't draw SVG text."""
import io
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "reference/fonts"
LOGO = ROOT / "tools/brand/columbia_logo.svg"
LOGO_PNG = ROOT / "godot_project/ui/brand/columbia_logo.png"
W, H = 1280, 800
NAVY = (22, 36, 68)
CREAM = (250, 240, 218)


def render_svg(path, width):
    with tempfile.TemporaryDirectory() as d:
        conf = Path(d) / "fonts.conf"
        conf.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>'
                        '<include ignore_missing="yes">/etc/fonts/fonts.conf</include>'
                        f'<dir>{FONTS}</dir><cachedir>{d}</cachedir></fontconfig>')
        png = subprocess.run(["rsvg-convert", "-w", str(width), str(path)], check=True,
                             capture_output=True, env={"FONTCONFIG_FILE": str(conf)}).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def shadowed_text(base, xy, s, f, fill):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((xy[0] + 2, xy[1] + 2), s, font=f, fill=NAVY + (200,))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(2)))
    ImageDraw.Draw(base).text(xy, s, font=f, fill=fill)


def main(art, out):
    im = Image.open(art).convert("RGB")
    scale = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    top = (im.height - H) // 2
    im = im.crop((0, top, W, top + H)).convert("RGBA")

    render_svg(LOGO, 1200).save(LOGO_PNG)
    logo = render_svg(LOGO, 640)
    x, y = 24, H - logo.height - 58
    # a soft navy pool under the logo so it holds against the painted fields
    pool = Image.new("L", (W, H), 0)
    ImageDraw.Draw(pool).ellipse((x - 120, y + 40, x + logo.width + 80, H + 140), fill=150)
    pool = pool.filter(ImageFilter.GaussianBlur(60))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, H), NAVY + (255,)),
                                       Image.new("RGBA", (W, H), (0, 0, 0, 0)), pool))
    im.alpha_composite(logo, (x, y))
    lob = ImageFont.truetype(str(FONTS / "Lobster-Regular.ttf"), 24)
    tag = "The pride of Middle America, bound for the stars"
    tw = ImageDraw.Draw(im).textlength(tag, font=lob)
    shadowed_text(im, (x + (logo.width - tw) / 2, H - 52), tag, lob, CREAM)
    im.convert("RGB").save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
