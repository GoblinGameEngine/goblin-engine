"""Compose the boot splash: Grok's pin-up art (reference/grok/splash) + our title type.

usage: python3 tools/brand/make_splash.py ART.jpg OUT.png   (art: Grok, briefs in tools/brand/splash_brief*.md;
       the art in use is reference/grok/splash/r2_img1.jpg, OUT = godot_project/ui/pda/splash.png)
Fonts are the OFL faces in reference/fonts (Limelight, Lobster)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "reference/fonts"
W, H = 1280, 800
NAVY = (22, 36, 68)
CREAM = (250, 240, 218)
CORAL = (214, 82, 64)
GOLD = (222, 168, 72)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def text_shadowed(base, xy, s, f, fill, shadow=NAVY, off=(4, 4), blur=3, stroke=0, stroke_fill=None):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((xy[0] + off[0], xy[1] + off[1]), s, font=f, fill=shadow + (170,),
           stroke_width=stroke, stroke_fill=shadow + (170,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)
    ImageDraw.Draw(base).text(xy, s, font=f, fill=fill, stroke_width=stroke,
                              stroke_fill=stroke_fill or fill)


def main(art, out):
    im = Image.open(art).convert("RGB")
    scale = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    top = (im.height - H) // 2
    im = im.crop((0, top, W, top + H)).convert("RGBA")

    # soft cream wash behind the title so it reads over the clouds and the window frame
    wash = Image.new("L", (W, H), 0)
    ImageDraw.Draw(wash).ellipse((-260, -220, 640, 330), fill=150)
    wash = wash.filter(ImageFilter.GaussianBlur(70))
    im.alpha_composite(Image.composite(Image.new("RGBA", (W, H), CREAM + (255,)),
                                       Image.new("RGBA", (W, H), (0, 0, 0, 0)), wash))

    x = 44
    text_shadowed(im, (x + 4, 28), "Welcome aboard", font("Lobster-Regular.ttf", 54), CORAL,
                  off=(2, 3), blur=2)
    text_shadowed(im, (x, 96), "SPACE STATION", font("Limelight-Regular.ttf", 40), NAVY,
                  shadow=(120, 90, 50), off=(2, 2), blur=1)
    text_shadowed(im, (x - 4, 132), "COLUMBIA", font("Limelight-Regular.ttf", 96), GOLD,
                  off=(5, 5), blur=3, stroke=3, stroke_fill=NAVY)
    text_shadowed(im, (x + 2, 252), "The pride of Middle America, bound for the stars",
                  font("Lobster-Regular.ttf", 26), NAVY, shadow=CREAM, off=(1, 1), blur=1)

    # loading line, bottom-left over the window frame
    text_shadowed(im, (x, H - 52), "loading the station...", font("Limelight-Regular.ttf", 24),
                  CREAM, off=(2, 2), blur=2)
    im.convert("RGB").save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
