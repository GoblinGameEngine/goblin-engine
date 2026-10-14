"""
sky_dress2.py -- a sky island model's dressing from the shared component library (remake/blender/sky/components via
sky_components; research/sky_islands/architecture/00_brief.md "Round-2 build contract").  Version 2 of gen/sky.py's
dress(): the first pass read as plain slabs in game (the user, 2026-10-14: "Each island needs to be fascinating ...
the most visually interesting parts of the map"), so here each style is spelled out with its own pieces, at a scale
that carries across the sky:

  windows     the style's signature bay on most upper windows -- roshan / mashrabiya / jharokha / glazed galeria /
              capsule / bay box -- or its balcony, else its screen, grille, shutters; a chhajja or eyebrow over each
  walls       a band at every floor (ablaq, inlay, plaster, timber ...); jetties (timber floors and corbels) on the
              jettied styles; full-width galleries on the gallery styles
  tiers       pagoda styles: big flared tile eaves round every block at every second floor and at the top
  roofs       the style's parapet (crenels, rounded merlons, screens, jali) on flat roofs; pitched side blocks under a
              hip / gable / chalet roofpiece; gables (stepped, neck, bell, cornice, false fronts) and hoist beams on the
              gable rows; domes, chhatris and towers (minarets, tapered kasbah corners, belfries, clocks) where the
              style has them; the roof clutter it lists (tanks, drums, shacks, lofts, antennas, laundry, chimneys,
              shrines, rebar, pergolas, altanas)
  street      awnings over the storefronts and lanterns at their doors
  light       the style's light strings (festoons, jhalar, bunting, luminarie, marquee and eave bulbs, LED bands) along
              the fronts, blade / stack / board signs and a rooftop billboard where it advertises -- the components'
              anchors (sign_*, glow_*, lights_*) go to the island's lights (SkySigns)

Parts (gblod's rules by name): "trim_skydress" (bays, balconies, bands, parapets: their hulls at LOD1, gone at LOD2 where
the blocks stand in), "windows_sky" (small: screens, shutters, lamps, clutter -- gone past full detail), "sky_roof-col"
(the silhouette: domes, towers, roofpieces, pagoda eave tiers, gables, shacks -- island hulls at LOD2; solid).
"""
import math
import os
import re

from mathutils import Matrix

import sky_components as SC

BIG, SMALL, ROOF = "trim_skydress", "windows_sky", "sky_roof-col"
BAY, PROXY = "windows_skybay", "trim_skyproxy"     # (detailed bays dropped past full detail; a box each stands in)
SIDES = {"S": (0, -1), "N": (0, 1), "E": (1, 0), "W": (-1, 0)}

ORIELS = ("roshan_bay", "mashrabiya_box", "jharokha", "galeria_glazed", "capsule_box", "bay_window_box")
BALCONIES = ("balcony_cage", "balcony_iron", "balcony_timber_covered", "balcony_curved", "balcony_fretwork",
             "balcony_band", "balcony_cantilever")
GALLERIES = ("gallery_iron", "gallery_timber", "gallery_rail")
PARAPETS = ("parapet_crenel", "parapet_rounded", "parapet_screen", "jali_parapet")
DOMES = ("dome_onion", "dome_ribbed", "dome_small", "dome_skylight")
TOWERS = ("tower_corner_tapered", "minaret_pyramid", "minaret_small", "menzeh_tower", "bell_tower", "clock_tower",
          "round_tower", "tower_square")
GABLES = ("gable_step", "gable_neck", "gable_bell", "gable_cornice", "false_front")
EAVES_TIER = ("eave_stack", "green_tile_eave", "barrel_tile_eave", "dragon_back_eave")
CLUTTER = ("water_tank", "water_drum", "rooftop_shack", "pigeon_loft", "antenna", "laundry_line", "trencadis_chimney",
           "chimney_stack", "roof_shrine", "rebar_stubs", "timber_pergola", "altana_deck", "roof_chalet", "vent_stack",
           "ac_unit")
LIGHTS = ("lights_jhalar", "luminarie_arch", "marquee_bulbs", "lights_festoon", "bunting", "eave_bulbs", "led_band",
          "lights_outline", "lights_fairy", "neon_outline")
SIGNS_TALL = ("sign_vertical_stack", "sign_blade", "neon_frame", "lightbox_sign", "dot_matrix_board", "sign_board",
              "painted_board", "brass_letters_set", "name_letters")
LAMPS = ("lantern_star", "lantern_cn", "lantern_paper", "lantern_star_paper", "lantern_wall", "lantern")
AWNINGS = ("awning", "noren", "shopfront_shutter", "boardwalk_awning")


def _comps(st):
    return set(st.get("components", [])) | set(st.get("roof", [])) | set(st.get("openings", []))


def _first(comps, ids, default=None):
    return next((i for i in ids if i in comps), default)


def _all(comps, ids):
    return [i for i in ids if i in comps]


def frame(x, y, z, out=(0, 1)):
    """component frame: origin (x, y, z), +Y turned to face out (dx, dy)"""
    th = math.atan2(-out[0], out[1])
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(th, 4, "Z")


def _q(v, step=0.1):
    return round(round(v / step) * step, 3)


def _edge(rect, side):
    x0, y0, x1, y1 = rect
    return {"S": ((x0, y0), (x1, y0)), "N": ((x1, y1), (x0, y1)), "E": ((x1, y0), (x1, y1)), "W": ((x0, y1), (x0, y0))}[side]


def _covered(blocks, bl, side, p, z):
    for ob in blocks:
        if ob is bl:
            continue
        ox0, oy0, ox1, oy1 = ob["rect"]
        if z > ob["wall_top"]:
            continue
        if side in "NS" and abs(p[1] - (oy0 if side == "N" else oy1)) < 0.05 and ox0 - 0.3 < p[0] < ox1 + 0.3:
            return True
        if side in "EW" and abs(p[0] - (ox0 if side == "E" else ox1)) < 0.05 and oy0 - 0.3 < p[1] < oy1 + 0.3:
            return True
    return False


def _roll(*k):
    return (hash(k) % 10007) / 10007.0


class Dresser:
    def __init__(self, b, tr, st, blocks):
        self.b, self.tr, self.st, self.blocks = b, tr, st, blocks
        self.sid = tr["style"]
        self.arch = tr.get("arch", "slab")
        self.c = _comps(st)
        self.rc = SC.recipe(self.sid)
        self.dens = float(tr.get("signage", {}).get("density", st.get("signage", {}).get("density", 0.5)))
        self.wall_mat = {}

    def put(self, part, cid, fr, size=None, variant=None, block=None, **kw):
        mat = {"trim": "trim"}                       # (the building's own light trim: whitewashed bands, crowns, frames)
        if block is not None:
            mat["wall"] = block["ext"]
        try:
            return SC.place(self.b, part, cid, fr, size=size, variant=variant, palette=self.sid, mat=mat, **kw)
        except Exception as e:                       # (one odd piece must not lose the building)
            print(f"sky_dress2: {cid} failed: {e}")
            return []

    def proxy(self, fr, w, d, h, mat):
        """a plain box (w along the wall, d out from it, h up) just inside a detailed bay: what LOD1 keeps of it"""
        p = self.b.part(PROXY)
        lo = fr @ Matrix.Translation((-w / 2, 0.02, 0.03))
        x0 = lo.to_translation()
        ux, uy = fr.col[0].to_3d(), fr.col[1].to_3d()
        corners = [x0, x0 + ux * w, x0 + ux * w + uy * d, x0 + uy * d]
        pts = [(c.x, c.y) for c in corners]
        if (corners[1] - corners[0]).cross(corners[3] - corners[0]).z < 0:
            pts = pts[::-1]
        p.prism(pts, x0.z, x0.z + h, mat)

    # ---------------------------------------------------------------- windows
    def windows(self, wins):
        c, rc = self.c, self.rc
        oriel = _first(c, ORIELS)
        balcony = _first(c, BALCONIES)
        o_share = 0.0 if oriel is None else (0.7 if self.arch in ("tower_cluster",) or oriel in ("roshan_bay", "mashrabiya_box", "jharokha") else 0.45)
        b_share = 0.0 if balcony is None else (0.55 if balcony in ("balcony_cage",) else 0.35)
        for w in wins:
            if w["shop"] or w["floor"] < 1:
                continue
            out = w["out"]
            bl = w["block"]
            ww, hh = _q(w["w"]), _q(w["h"])
            sill = w["z"] - hh / 2
            fz = bl["floors"][w["floor"]][0]
            roll = _roll(self.sid, round(w["x"], 1), round(w["y"], 1), w["floor"])
            front = w["side"] == "N"
            if roll < o_share and (front or roll < o_share * 0.6):
                ow, oh = _q(ww + 0.6), _q(hh + 0.7)
                self.put(BAY, oriel, frame(w["x"], w["y"], sill - 0.3, out), size=(ow, oh, 0.85), block=bl)
                self.proxy(frame(w["x"], w["y"], sill - 0.3, out), ow - 0.06, 0.8, oh - 0.06, bl["ext"])
                continue
            if roll < o_share + b_share and front:
                bw = _q(ww + 1.4)
                self.put(BAY, balcony, frame(w["x"], w["y"], fz + 0.05, out), size=(bw, None, 1.1), block=bl)
                self.proxy(frame(w["x"], w["y"], fz - 0.1, out), bw - 0.06, 1.05, 0.12, "trim")
            elif rc.get("grille") and roll > 0.5:
                self.put(SMALL, rc["grille"], frame(w["x"], w["y"], sill, out), size=(_q(ww + 0.1), _q(hh * 0.95)))
            elif "screen" in rc and any(k in c for k in ("screen_lattice", "jali_screen", "grille_geometric", "mashrabiya_box")):
                self.put(SMALL, rc["screen"], frame(w["x"], w["y"], sill, out), size=(ww, _q(hh * 0.9)))
            if rc.get("shutters"):
                for sx in (-1, 1):
                    ox, oy = -out[1] * sx * (ww / 2 + 0.28), out[0] * sx * (ww / 2 + 0.28)
                    self.put(SMALL, "shutters", frame(w["x"] + ox, w["y"] + oy, sill, out), size=(_q(ww / 2), _q(hh * 0.9)))
            if rc.get("eave"):
                self.put(SMALL, rc["eave"], frame(w["x"], w["y"], sill + hh + 0.15, out), size=(_q(ww + 0.6), 0.3, 0.55))
            if rc.get("ac") and not front and roll > 0.6:
                ox, oy = -out[1] * (ww / 2 + 0.6), out[0] * (ww / 2 + 0.6)
                self.put(SMALL, "ac_unit", frame(w["x"] + ox, w["y"] + oy, sill - 0.2, out), size=(0.7, 0.5, 0.35))

    # ---------------------------------------------------------------- walls: bands, jetties, galleries, tiers
    def walls(self):
        c, rc = self.c, self.rc
        band = rc.get("band") or ("plaster_band" if self.st.get("region") in ("arabian", "indian") else None)
        jetty = "jetty_upper" in c or self.sid in ("jetty_lanes", "ablaq_lanes", "medina_warren")
        gallery = _first(c, GALLERIES)
        tier = _first(c, EAVES_TIER) or ("green_tile_eave" if self.arch == "pagoda" else None)
        cell = _first(c, ("ghorfa_vault", "vault_cell", "box_module", "souk_vault")) if self.arch == "pile" else None
        for bl in self.blocks:
            for side, out in SIDES.items():
                a, e = _edge(bl["rect"], side)
                L = _q(math.dist(a, e))
                mx, my = (a[0] + e[0]) / 2, (a[1] + e[1]) / 2
                n = len(bl["floors"])
                for k, (fz, cz) in enumerate(bl["floors"]):
                    if k == 0:
                        continue
                    z = fz - 0.25
                    if _covered(self.blocks, bl, side, (mx, my), z + 0.6):
                        continue
                    if band and (k % 2 == 1 or n <= 4):
                        self.put(SMALL, band, frame(mx, my, z, out), size=(L, 0.28), block=bl)
                    if jetty and side == "N":
                        self.put(BAY, "jetty_upper", frame(mx, my, fz - 0.05, out), size=(L, None, 0.55), block=bl)
                    if gallery and side == "N" and bl is self.blocks[0]:
                        self.proxy(frame(mx, my, fz - 0.1, out), L - 0.1, 1.35, 0.12, "trim")
                        self.put(BAY, gallery, frame(mx, my, fz + 0.02, out), size=(L, None, 1.4), block=bl)
                    if cell and side == "N":
                        # the honeycomb: cells stacked up the front, staggered floor by floor
                        nc = max(1, int(L / 3.4))
                        for j in range(nc):
                            if (j + k) % 2:
                                continue
                            t = (j + 0.5) / nc - 0.5
                            px, py = mx - out[1] * t * L, my + out[0] * t * L
                            self.put(BAY, cell, frame(px, py, fz + 0.05, out), size=(2.8, 2.5, 1.3), block=bl)
                            self.proxy(frame(px, py, fz + 0.05, out), 2.74, 1.25, 2.44, bl["ext"])
                    if self.arch == "pagoda" and tier and (k % 2 == 0):
                        self.put(ROOF, tier, frame(mx, my, fz - 0.15, out), size=(_q(L + 2.4), 0.7, 1.7), variant="slab", block=bl)
                top = bl["wall_top"]
                # the tower towns' crowns: a broad whitewashed band at the top of every tower (Sana'a, Shibam, the kasbahs)
                if self.arch == "tower_cluster" and not _covered(self.blocks, bl, side, (mx, my), top - 0.5):
                    self.put(BIG, "plaster_band", frame(mx, my, top - 1.3, out), size=(L, 1.3), block=bl)
                if self.arch == "pagoda" and tier and not _covered(self.blocks, bl, side, (mx, my), top + 0.5):
                    self.put(ROOF, tier, frame(mx, my, top - 0.1, out), size=(_q(L + 3.0), 0.9, 2.1), variant="slab", block=bl)

    # ---------------------------------------------------------------- roofs
    def roofs(self):
        c = self.c
        parapet = _first(c, PARAPETS)
        dome = _first(c, DOMES) or ("dome_small" if self.tr.get("model_kind") in ("hall",) and self.st.get("region") in ("arabian", "indian") else None)
        tower = _first(c, TOWERS)
        gable = _first(c, GABLES) or ("gable_step" if self.arch == "gable_row" else None)
        clutter = _all(c, CLUTTER)
        model = self.tr.get("model_kind", "")
        main = self.blocks[0]
        for bi, bl in enumerate(self.blocks):
            x0, y0, x1, y1 = bl["rect"]
            W, D = x1 - x0, y1 - y0
            top = bl["wall_top"]
            par = bl["roof"]["parapet"]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            # the parapet round a flat roof (not on the fire escape's side of the main block)
            if not bl.get("pitched") and parapet:
                for side, out in SIDES.items():
                    if bl is main and side == "E":
                        continue
                    a, e = _edge(bl["rect"], side)
                    mx, my = (a[0] + e[0]) / 2, (a[1] + e[1]) / 2
                    if _covered(self.blocks, bl, side, (mx, my), top + 0.8):
                        continue
                    self.put(BIG, parapet, frame(mx, my, top + par, out), size=(_q(math.dist(a, e)), 0.9), block=bl)
            # a pitched side block: its roofpiece
            if bl.get("pitched"):
                pk = bl["pitched"]
                cid = pk if pk in ("roof_chalet", "stone_slab_roof") else "roofpiece"
                variant = None if cid != "roofpiece" else ("hip" if pk in ("hip",) else "gable")
                self.put(ROOF, cid, frame(cx, cy, top + par, (0, 1)), size=(_q(W + 0.8), _q(min(W, D) * 0.38), _q(D + 0.8)),
                         variant=variant, block=bl)
                continue
            # gable rows: a gable over every block's front, a hoist beam in it
            if gable and self.arch == "gable_row":
                gh = _q(min(W * 0.75, 6.0))
                self.put(ROOF, gable, frame(cx, y1, top + par * 0.0, (0, 1)), size=(_q(W), gh), block=bl)
                if "hoist_beam" in c or self.sid in ("hoist_gables", "gard_wharf"):
                    self.put(BIG, "hoist_beam", frame(cx, y1, top + gh * 0.55, (0, 1)), size=(0.25, 0.5, 1.2))
                if bl is not main:
                    continue
            if gable == "false_front" and bl is main and self.arch != "gable_row":
                self.put(ROOF, "false_front", frame(cx, y1, top, (0, 1)), size=(_q(W), _q(min(W * 0.3, 3.5))), block=bl)
            # domes, towers, chhatris
            big = min(W, D)
            spots = [(x0 + 1.6, y0 + 1.6), (x0 + 1.6, y1 - 1.6), (x1 - 1.6, y1 - 1.6), (x1 - 1.6, y0 + 1.6)]
            if bl is main:
                spots = spots[:2]                    # (+x: the fire escape's platform; the middle: a lark's cradle)
            if dome and (model in ("hall", "landmark") or bi == len(self.blocks) - 1) and big >= 7.5 and not (bl is main and big >= 15):
                dw = _q(big * 0.62)
                self.put(ROOF, dome, frame(cx, cy, top + par * 0.0, (0, 1)), size=(dw, dw, dw), block=bl)
                spots = [p for p in spots if math.dist(p, (cx, cy)) > dw * 0.5 + 1.2]
            if tower == "tower_corner_tapered":
                for (sx, sy) in spots[:4]:
                    self.put(ROOF, tower, frame(sx, sy, top, (0, 1)), size=(2.2, _q(3.0 + len(bl["floors"]) * 0.5), 2.2), block=bl)
                spots = []
            elif tower and (model == "landmark" and bl is main or model == "hall" and bi == 0):
                sx, sy = spots.pop(0) if spots else (cx, cy)
                self.put(ROOF, tower, frame(sx, sy, top, (0, 1)), size=(2.6, _q(6.0 + len(bl["floors"]) * 0.6), 2.6), block=bl)
            if "chhatri" in c:
                for (sx, sy) in spots[:2]:
                    self.put(ROOF, "chhatri", frame(sx, sy, top, (0, 1)), size=(2.6, 3.6, 2.6))
                spots = spots[2:]
            # the clutter: what this style keeps on its roofs, a few to a roof
            for k, cid in enumerate(clutter[:len(spots)]):
                sx, sy = spots[k]
                self.put(SMALL if cid in ("antenna", "laundry_line", "ac_unit", "rebar_stubs") else ROOF, cid,
                         frame(sx, sy, top, (0, 1)))

    # ---------------------------------------------------------------- street and light
    def street(self, shops_by_block):
        c = self.c
        aw = _first(c, AWNINGS) or ("awning" if self.dens >= 0.5 else None)
        lamp = _first(c, LAMPS)
        for bl in self.blocks:
            fz = bl["floors"][0][0]
            y1 = bl["rect"][3]
            for s in shops_by_block.get(bl["name"], []):
                w = _q(s["x1"] - s["x0"] - 0.4)
                if aw == "awning" or aw == "boardwalk_awning":
                    self.put(SMALL, "awning", frame((s["x0"] + s["x1"]) / 2, y1, fz + 2.7, (0, 1)), size=(w, 1.1, 1.3))
                elif aw == "noren":
                    self.put(SMALL, "noren", frame(s["door"], y1, fz + 2.3, (0, 1)), size=(1.4, 0.9))
                if lamp:
                    for dx in (-0.9, 0.9):
                        self.put(SMALL, lamp, frame(s["door"] + dx, y1, fz + 2.25, (0, 1)))

    def lights(self):
        c = self.c
        runs = _all(c, LIGHTS) or (["lights_festoon"] if self.dens >= 0.5 else [])
        sign = _first(c, SIGNS_TALL) or ("sign_blade" if self.dens >= 0.5 else "sign_board")
        model = self.tr.get("model_kind", "")
        for bi, bl in enumerate(self.blocks):
            x0, y0, x1, y1 = bl["rect"]
            W = x1 - x0
            n = len(bl["floors"])
            cx = (x0 + x1) / 2
            for k, (fz, cz) in enumerate(bl["floors"]):
                if k == 0 or not runs:
                    continue
                if k % 2 == 0 or k == n - 1:
                    cid = runs[(k + bi) % len(runs)]
                    self.put(SMALL, cid, frame(cx, y1 + 0.02, fz - 0.3, (0, 1)), size=(_q(W - 0.4), 0.3, 0.1))
            if runs:
                self.put(SMALL, runs[bi % len(runs)], frame(cx, y1 + 0.02, bl["wall_top"] + bl["roof"]["parapet"] + 0.05, (0, 1)),
                         size=(_q(W), 0.3, 0.1))
            # signs up the front: a blade or stack at the front corner of every block of 3+ storeys
            if n >= 3 and self.dens >= 0.3:
                hh = _q(min(n * 1.6, 10.0))
                sx = x0 + 0.6 if bi % 2 else x1 - 0.6
                self.put(SMALL, sign, frame(sx, y1, bl["floors"][1][0] + 0.2, (0, 1)),
                         size=(1.0, hh, 0.2) if sign in ("sign_vertical_stack", "sign_blade") else (_q(min(W - 1.0, 4.0)), 1.0, 0.2))
        if model in ("landmark", "tall") and self.dens >= 0.45 or "rooftop_billboard" in c:
            main = self.blocks[-1] if len(self.blocks) > 1 else self.blocks[0]
            x0, y0, x1, y1 = main["rect"]
            bw = _q(min(x1 - x0 - 1.0, 9.0))
            self.put(ROOF, "rooftop_billboard", frame((x0 + x1) / 2, y0 + 2.0, main["wall_top"] + main["roof"]["parapet"], (0, 1)),
                     size=(bw, _q(bw * 0.42), 0.4))


def _anchor_rows(b):
    """the components' anchor empties -> the island's anchor rows [name, x, y, z, yaw] in the building's Godot frame"""
    import bpy
    rows = []
    for n in getattr(b, "sky_anchors", []):
        e = bpy.data.objects.get(n)
        if e is None:
            continue
        M = e.matrix_world
        p = M.to_translation()
        oy = M.col[1].to_3d()                         # (the face's out is the empty's -Y)
        out = (-oy.x, -oy.y)
        yaw = math.atan2(out[0], -out[1])
        name = re.sub(r"\.\d{3}$", "", n)              # (Blender's duplicate suffix only: the sizes have decimals)
        rows.append([name, round(p.x, 2), round(p.z, 2), round(-p.y, 2), round(yaw, 4)])
    return rows


def dress(b, tr, st, blocks, wins, shops_by_block, anchors, rnd):
    d = Dresser(b, tr, st, blocks)
    d.windows(wins)
    d.walls()
    d.roofs()
    d.street(shops_by_block)
    d.lights()
    # every storefront's own sign (the shop's name: SkySigns) over its door, as before
    kinds = tr.get("signage", {}).get("kinds") or ["lightbox"]
    n = 0
    for bl in blocks:
        y1 = bl["rect"][3]
        fz = bl["floors"][0][0]
        for s in shops_by_block.get(bl["name"], []):
            sw = _q(min(s["x1"] - s["x0"] - 0.8, 7.0))
            kind = kinds[n % len(kinds)]
            anchors.append([f"sign_{kind}_{sw}x1.1"] + [round((s["x0"] + s["x1"]) / 2, 2), round(fz + 3.0, 2), round(-(y1 + 0.08), 2), 3.1416])
            n += 1
    anchors.extend(_anchor_rows(b))
    b.sky_roof = b.part(ROOF)


SKY_CEIL = (("pressed_tin_ceiling", "pressed_tin"), ("pressed_tin", "pressed_tin"), ("artesonado_ceiling", "artesonado_coffer"),
            ("coffered_ceiling", "coffered"), ("batten_ceiling", "batten"))


def ceilings(b, tr, st, spec, blocks):
    """THE CEILING TILES (the user asked for a model): the style's ceiling in every shop and hall (SC.ceiling)"""
    c = _comps(st)
    v = next((v for k, v in SKY_CEIL if k in c), None) or {"tokyo": "batten", "spanish": "artesonado_coffer",
                                                           "europe": "pressed_tin", "canada": "pressed_tin"}.get(st.get("region"), "suspended_grid_600")
    for r in spec["rooms"]:
        if r.get("type") not in ("shop", "hall", "market", "store") or r.get("floor", 0) != 0:
            continue
        x0, y0, x1, y1 = r["rect"]
        bl = next((bl for bl in blocks if bl["rect"][0] - 0.05 <= (x0 + x1) / 2 <= bl["rect"][2] + 0.05
                   and bl["rect"][1] - 0.05 <= (y0 + y1) / 2 <= bl["rect"][3] + 0.05), blocks[0])
        cz = bl["floors"][0][1] - 0.05
        try:
            SC.ceiling(b, "fit_sky_ceiling", (x0 + 0.05, y0 + 0.05, x1 - 0.05, y1 - 0.05), cz, v, palette=tr["style"])
        except Exception as e:
            print(f"sky_dress2: ceiling failed: {e}")
