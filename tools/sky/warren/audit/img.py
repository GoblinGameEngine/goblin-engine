"""img.py -- small PNG drawings (PIL) an AI can read: orthographic views of a part against its boxes, and a plan
canvas for island heat maps.

  views(tris, boxes, path, red=None, title="")    front (x-y), side (z-y), top (x-z) of tris; boxes [(lo, hi, rgb,
                                                  label)]; triangles in `red` drawn red
  Plan(x0, z0, xlen, zlen, px)                        a top-down canvas in the island frame (x down the page = +X south,
                                                  z across = +Z west, as the plan strings read)
"""
import numpy as np
from PIL import Image, ImageDraw

VIEWS = (("front  x->  y^", 0, 1), ("side  z->  y^", 2, 1), ("top  x->  z^", 0, 2))


def views(tris, boxes, path, red=None, title="", size=300, pad=0.25):
    t = np.asarray(tris, float)
    pts = [t.reshape(-1, 3)] + [np.array([lo, hi], float) for lo, hi, *_ in boxes]
    allp = np.concatenate([p for p in pts if len(p)])
    lo, hi = allp.min(0) - pad, allp.max(0) + pad
    redset = set(np.asarray(red if red is not None else [], int).tolist())
    W = size * 3 + 40
    im = Image.new("RGB", (W, size + 50), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    dr.text((6, 4), title, fill=(0, 0, 0))
    for v, (name, a, b) in enumerate(VIEWS):
        ox = 10 + v * (size + 10)
        oy = 30
        span = max(hi[a] - lo[a], hi[b] - lo[b])
        sc = size / span

        def P(x, y):
            return (ox + (x - lo[a]) * sc, oy + size - (y - lo[b]) * sc)
        dr.rectangle([ox, oy, ox + size, oy + size], outline=(200, 200, 200))
        dr.text((ox + 4, oy + 4), name, fill=(90, 90, 90))
        # grid every 0.5 m
        for gx in np.arange(np.ceil(lo[a] * 2) / 2, hi[a], 0.5):
            dr.line([P(gx, lo[b]), P(gx, hi[b])], fill=(235, 235, 235))
        for gy in np.arange(np.ceil(lo[b] * 2) / 2, hi[b], 0.5):
            dr.line([P(lo[a], gy), P(hi[a], gy)], fill=(235, 235, 235))
        dr.line([P(0, lo[b]), P(0, hi[b])], fill=(210, 210, 255))
        dr.line([P(lo[a], 0), P(hi[a], 0)], fill=(210, 210, 255))
        for k, tri in enumerate(t):
            poly = [P(p[a], p[b]) for p in tri]
            if k in redset:
                continue
            dr.polygon(poly, fill=(205, 205, 205), outline=(150, 150, 150))
        for k in redset:
            poly = [P(p[a], p[b]) for p in t[k]]
            dr.polygon(poly, fill=(255, 120, 120), outline=(220, 0, 0))
        for lo_b, hi_b, rgb, label in boxes:
            dr.rectangle([P(lo_b[a], hi_b[b]), P(hi_b[a], lo_b[b])], outline=tuple(rgb), width=2)
    y = size + 34
    x = 10
    for _, _, rgb, label in boxes:
        dr.rectangle([x, y + 2, x + 10, y + 10], outline=tuple(rgb), width=2)
        dr.text((x + 14, y), label, fill=(0, 0, 0))
        x += 14 + 7 * len(label) + 16
    dr.rectangle([x, y + 2, x + 10, y + 10], fill=(255, 120, 120), outline=(220, 0, 0))
    dr.text((x + 14, y), "outside", fill=(0, 0, 0))
    im.save(path)
    return path


class Plan:
    """a top-down canvas: pixel (col, row) = (z, x) so it reads like the twin's plan strings (row = i = +X)"""

    def __init__(self, x0, z0, xlen, zlen, px=0.5, bg=(255, 255, 255)):
        self.x0, self.z0, self.px = x0, z0, px
        self.W, self.H = int(np.ceil(zlen / px)), int(np.ceil(xlen / px))   # columns along z, rows along x
        self.im = Image.new("RGB", (self.W, self.H), bg)
        self.dr = ImageDraw.Draw(self.im)

    def xy(self, x, z):
        return ((z - self.z0) / self.px, (x - self.x0) / self.px)

    def raster(self, rgb):
        """rgb (rows = x, cols = z, 3) uint8 at the canvas resolution"""
        self.im.paste(Image.fromarray(rgb, "RGB"), (0, 0))
        self.dr = ImageDraw.Draw(self.im)

    def line(self, a, b, rgb, w=1):
        self.dr.line([self.xy(a[0], a[2]), self.xy(b[0], b[2])], fill=tuple(rgb), width=w)

    def dot(self, p, rgb, r=3, outline=None):
        c = self.xy(p[0], p[2])
        self.dr.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=tuple(rgb), outline=outline)

    def cross(self, p, rgb, r=4, w=2):
        c = self.xy(p[0], p[2])
        self.dr.line([(c[0] - r, c[1] - r), (c[0] + r, c[1] + r)], fill=tuple(rgb), width=w)
        self.dr.line([(c[0] - r, c[1] + r), (c[0] + r, c[1] - r)], fill=tuple(rgb), width=w)

    def text(self, p, s, rgb=(0, 0, 0)):
        self.dr.text(self.xy(p[0], p[2]), s, fill=tuple(rgb))

    def legend(self, items, title=""):
        """items [(rgb, label)] in a strip added under the plan"""
        h = 16 * (len(items) + 2)
        out = Image.new("RGB", (max(self.W, 420), self.H + h), (255, 255, 255))
        out.paste(self.im, (0, 0))
        dr = ImageDraw.Draw(out)
        y = self.H + 4
        dr.text((4, y), title, fill=(0, 0, 0))
        for rgb, label in items:
            y += 16
            dr.rectangle([6, y + 2, 16, y + 12], fill=tuple(rgb))
            dr.text((22, y), label, fill=(0, 0, 0))
        self.im = out
        self.dr = ImageDraw.Draw(self.im)

    def save(self, path):
        self.im.save(path)
        return path
