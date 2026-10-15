"""The Civ base: its palette, growth params, and the hooks the generic passes call.

A face context (`ctx`) passed to the facade hooks:
    level, ground (bool: the column's ground floor), use (HOME/SHOP/...), epoch, outward (what the face looks onto:
    'main' 'plaza' 'artery' 'lane' 'court' 'green' 'rim' 'void' 'air' 'gate' 'reserved' 'water'), lane_w (cells),
    door (bool: this face is the unit's door), stack (int: the face's column hash -- for vertical alignment),
    covered (bool: the lane outside is roofed over above), age (0 oldest .. 5 newest), i, j, rot.
A facade hook returns (piece_id, variant, palette_slot) or None for no piece.
"""


class Civ:
    id = "base"
    name = "base"
    lanes = "tree"                 # "tree" | "grid"
    palette = ["#cccccc"]          # up to 16 sRGB colours; slots index into it
    species = []                   # foliage species ids this civ plants
    params = {}

    def __init__(self, isl, rng):
        self.isl = isl
        self.rng = rng

    base_palette = 0               # the kit palette variant (pieces.json palettes[civ][n]) of public pieces

    def lot_palette(self, lot):
        """the kit palette variant of a whole house (never per cell: per-cell colours make stripes)"""
        return self.base_palette

    # slots: which palette entry fills a material slot
    def slot(self, name, epoch=1, ij=(0, 0)):
        return 0

    def facade(self, ctx):
        return ("wall_plain", 0, self.slot("wall", ctx["epoch"]))

    def corner(self, kind, level, epoch):
        return ("corner_out" if kind == "out" else "corner_in", 0, self.slot("wall", epoch))

    def roof_field(self, i, j, level, epoch):
        return ("roof_terrace", 0, self.slot("roof", epoch))

    def roof_edge(self, ctx):
        return ("parapet_plain", 0, self.slot("wall", ctx["epoch"]))

    def pave(self, L, plan_class, c, default):
        """the paving piece of an open cell"""
        return default

    def mark_lots(self, L, rng):
        """choose civic/special lots before the founding"""

    def marks(self, L, rng, emit):
        """signature pieces (minarets, fountains, roof villages ...)"""

    def overlay(self, L, rng, emit, cells):
        """E5, the newest layer: cables, AC, tanks, signs, lanterns ..."""

    def foliage(self, L, rng):
        return []
