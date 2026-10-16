"""kitmap.py -- the generator's piece choices to the KIT's real pieces (godot_project/remake/sky/warrens/pieces.json,
built by remake/blender/sky/warren_kit/build.py), in the kit's frames:

  face pieces (kind wall / edge / sign): the face plane at the origin, +Z out of the cell, x -1.5..1.5, y 0..3.2
  corner pieces: the origin on the cell's vertical edge, the occupied cell in -X/-Z
  cell pieces (everything else): the origin at the cell centre, y 0 the walking surface / roof top / ceiling

The generator works in its own convention (FACE: rot 0 the -Z face); the kit's rot is the generator's + 2 for faces,
corners and directional cell pieces alike (rot r turns the piece's +Z to +Z, +X, -Z, -X for r = 0..3).  The palette
nibble becomes the kit palette variant (pieces.json palettes[civ][n]) -- one per house (a lot), not per cell.
"""
import json
import os

from pieces import KIT_JSON


def load_kit():
    if not os.path.exists(KIT_JSON):
        return None
    return json.load(open(KIT_JSON))


def _thick(base, var, kit):
    """base + _k (thick, variant 1) or _t; falls back to the other thickness, then to the bare id"""
    want = base + ("_k" if var == 1 else "_t")
    other = base + ("_t" if var == 1 else "_k")
    for c in (want, other, base):
        if c in kit:
            return c
    return None


def kit_id(pid, var, civ_id, kit):
    """the kit piece for a generator piece (None: the kit has nothing for it -- dropped, reported)"""
    medina = civ_id == "maghrebi_medina"
    if pid in kit:
        return pid
    direct = {
        "roof_terrace": "roof_terrace", "roof_tile": "roof_tin", "soffit": "floor_slab",
        "interior_floor": "int_floor", "interior_ceiling": "int_ceiling", "counter": "int_counter",
        "shelves": "int_shelves", "table_set": "int_table_set", "bed": "int_bed", "lamp": "int_lamp",
        "pave_main": "pave_main", "pave_lane": "pave_lane", "pave_plaza": "pave_plaza", "pave_garden": "pave_garden",
        "pave_court": "pave_court", "steps": "steps_up", "step_low_1": "step_low_1", "step_low_4": "step_low_4", "stair_ext": "stair_run", "stair_spiral": "stair_spiral",
        "ladder": "ladder", "bridge_plank": "bridge_plank", "bridge_timber": "bridge_timber",
        "bridge_steel": "bridge_steel", "arcade_pier": "arcade_pier", "market_stall": "ov_stall",
        "awning": "ov_awning_cane", "planter": "ov_planter", "fountain_basin": "fountain_riad",
        "zellige_fountain": "fountain_riad", "cable_span": "ov_cables", "ac_unit": "ov_ac", "pipe_run": "ov_pipe_run",
        "water_tank": "ov_tank", "antenna": "ov_antennas", "satellite_dish": "ov_dish", "laundry": "ov_laundry",
        "lantern": "ov_lantern", "festoon": "ov_festoon", "fluoro_tube": "ov_fluoro", "sign_blade": "ov_sign_blade",
        "sign_box": "ov_sign_box", "sign_board": "ov_sign_board", "sign_arm": "ov_sign_arm",
        "shoring_beam": "shoring_beam", "sabat_beams": "sabat_beams", "alley_ceiling": "alley_ceiling",
        "minaret_base": "minaret_base", "minaret_square": "minaret_shaft", "minaret_top": "minaret_top",
        "roof_playground": "ov_playground", "warning_light": "ov_lantern", "green_hip": "green_hip",
        "crown_band": "crown_band", "dome_cap": "dome_cap", "wall_fountain": "wall_fountain_k",
        "kerb_straight": "kerb_straight", "kerb_out": "kerb_out", "kerb_in": "kerb_in", "kerb_post": "kerb_post",
        "ov_shack_a": "ov_shack_a", "ov_shack_b": "ov_shack_b", "ov_shack_c": "ov_shack_c",
        "corner_column": "corner_column", "edge_eave_tile_green": "edge_eave_tile_green",
        "edge_eave_tin": "edge_eave_tin",
    }
    if pid in direct:
        k = direct[pid]
        return k if k in kit else None
    walls = {
        "wall_plain": "wall_plain", "wall_window_s": "wall_window_s", "wall_window_m": "wall_window_m",
        "wall_window_l": "wall_window_l", "wall_window_pair": "wall_window_pair", "wall_door": "wall_door",
        "wall_shopfront": "wall_shopfront_a", "wall_shopfront_arcade": "wall_shopfront_b",
        "wall_screen": "wall_screen", "wall_balcony_cage": "wall_balcony_cage",
        "wall_balcony_timber": "wall_balcony_timber", "wall_balcony_iron": "wall_balcony_iron",
        "wall_bay": "wall_bay_box", "wall_oriel": "wall_bay_box", "wall_arch_round": "wall_arch_round",
        "wall_arch_pointed": "wall_arch_pointed", "wall_arch_horseshoe": "wall_arch_horseshoe",
        "wall_blind_arch": "wall_blind_arch", "wall_gallery": "wall_balcony_timber",
        "wall_cantilever_step": "wall_cantilever_step", "wall_tower_seam": "wall_tower_seam",
        "parapet_plain": "edge_parapet_plain", "parapet_crenel": "edge_parapet_crenel",
        "parapet_jali": "edge_parapet_jali", "parapet_rounded": "edge_parapet_rounded", "edge_rail": "edge_rail",
        "corner_out": "corner_quoin", "corner_round": "corner_round", "corner_chamfer": "corner_chamfer",
        "corner_in": "corner_in", "plinth": "plinth",
    }
    if pid == "wall_window_grille":
        return _thick("wall_window_grille", var, kit) if not medina else _thick("wall_window_s", 1, kit)
    if pid == "wall_door_studded":
        return "wall_door_portal_k" if "wall_door_portal_k" in kit else _thick("wall_door", 1, kit)
    if pid == "wall_zellij":
        return "wall_zellij_k" if "wall_zellij_k" in kit else _thick("wall_plain", 1, kit)
    if pid == "wall_qamariya":
        return "wall_qamariya_k" if "wall_qamariya_k" in kit else _thick("wall_window_m", 1, kit)
    if pid == "arch_mouth":
        return _thick("wall_arch_horseshoe" if medina else "wall_arch_round", var, kit)
    if pid in walls:
        return _thick(walls[pid], var, kit)
    return _thick(pid, var, kit)       # (a kit base id without its thickness suffix; None if the kit lacks it)      # (anything the kit lacks: reported)


FACE_KINDS = ("wall", "edge", "sign", "passage", "water_edge")
FACE_GEN = {0: (0, -1), 1: (-1, 0), 2: (0, 1), 3: (1, 0)}      # (the generator's FACE: pick.FACE)
FACE_HUNG = ("ov_ac", "ov_lantern", "ov_fluoro", "ov_planter", "ov_pipe_run", "ladder", "band_brick_relief",
             "edge_gable_step", "edge_gable_neck", "edge_gable_bell", "wall_sign_column_t", "ov_vending_machine",
             "hoist_beam", "drain_spout", "stair_steel_external", "ov_gold_eave_led", "ov_sign_arm_big",
             "ov_roller_shutter", "band_zocalo", "ov_blue_pots", "dukkana_bench", "ov_snow_cap",
             "ov_sign_vertical_stack", "ov_mastaba", "roshan_crest", "ov_marigold_garland", "band_flood",
             "ov_truck_art_panel", "ov_wedding_curtain", "edge_chhajja", "edge_horsehead_wall", "ov_machicolation",
             "stair_external_white", "roof_dormer_attic", "cesme_fountain", "band_damp", "band_peranakan_tile",
             "ov_wall_shrine", "ov_gold_shop_neon", "edge_pembe_frieze", "edge_firewall_gable")   # on a face plane
CORNER_HUNG = ("kerb_post", "corner_statue_niche", "ov_prayer_flag_pole")
ACROSS = ("ov_cables", "shoring_beam", "ov_festoon", "ov_chochin_string", "torii", "cable_car", "ov_toldo",
          "ov_suq_canopy", "ov_prayer_flags", "ov_wire_net", "tram_rail", "ov_jeepney", "ov_laundry_line_lane",
          "abbara_vault")      # spans laid along the kit's X: the generator's rot is the span's


def mount(kid, pieces):
    """0 cell (origin the cell centre), 1 face (the face plane: + translate(0, 0, 1.5) after the rot), 2 corner
    (+ translate(1.5, 0, 1.5) after the rot) -- FORMAT.md; also written into the variant nibble of every record"""
    kind = pieces[kid].get("kind")
    if kind == "corner" or kid in CORNER_HUNG:
        return 2
    if kind in FACE_KINDS or kid in FACE_HUNG:
        return 1
    return 0


def house_palette(L, civ, i, j, k):
    """the palette variant of the house this cell belongs to (a lot) -- whole houses, never single cells"""
    if L.inb(i, j) and 0 <= k < L.L and L.unit[i, j, k] >= 0:
        lot = L.unit_lot.get(int(L.unit[i, j, k]), int(L.lot[i, j]))
    else:
        lot = int(L.lot[i, j]) if L.inb(i, j) else -1
    if lot < 0:
        return civ.base_palette
    if hasattr(civ, "cell_palette"):
        return civ.cell_palette(L.lots[lot], k - int(L.gk[i, j]) if L.inb(i, j) else 0)
    return civ.lot_palette(L.lots[lot])


def translate(L, civ, recs, kit, shacks=()):
    """the generator's records -> kit records (kid, i, j, level, kit_rot, flags, mount, palette_variant, epoch);
    returns them and {generator piece: count} of what the kit has nothing for"""
    from lattice import ARTERY, CIVIC, LANE
    from pick import h01
    pieces = kit["pieces"]
    medina = civ.id == "maghrebi_medina"
    L.unit_lot = {}
    for lot in L.lots:
        if "unit" in lot:
            L.unit_lot[lot["unit"]] = lot["id"]
    for u, lid in getattr(L, "unit_lots", {}).items():
        L.unit_lot.setdefault(u, lid)
    out, dropped = [], {}
    shack_at = set((i, j, k) for (i, j, k) in shacks)
    mina = [r for r in recs if r[0] == "minaret_square"]
    mina_low = {(r[1], r[2]): min(q[3] for q in mina if (q[1], q[2]) == (r[1], r[2])) for r in mina}

    # the cells a stair's ramp meets (its head and its foot): their paving must be flush with the ramp's ends
    # (y 0 / the storey line): a raised paving top there (pave_garden +5 cm, brick +10 cm) is a lip the player's
    # capsule cannot roll over from a 28 deg ramp (the audit's strict walk; in game ~30-80 % of walks stuck there)
    ramp_ends = set()
    for (si, sj), st in getattr(L, "stair", {}).items():
        di, dj = FACE_GEN[st[0]]
        ramp_ends.add((si + di, sj + dj))
        ramp_ends.add((si - di, sj - dj))
    L.flush_swapped = 0

    def flush(kid, i, j):
        sp = pieces.get(kid, {})
        if sp.get("kind") != "ground" or (i, j) not in ramp_ends or sp.get("bounds", [[0, 0, 0], [0, 0, 0]])[1][1] <= 0.01:
            return kid
        for c in (("pave_lane_skirt", "pave_lane") if kid.endswith("_skirt") else ("pave_lane",)):
            if c in pieces and pieces[c].get("bounds", [[0, 0, 0], [0, 1, 0]])[1][1] <= 0.01:
                L.flush_swapped += 1
                return c
        return kid

    def put(kid, i, j, lv, rot, flags, ep, pal=None, kit_rot=None):
        if kid not in pieces and kid.endswith("_skirt") and kid[:-6] in pieces:
            kid = kid[:-6]                                  # (a civ paving with no skirted twin: the plain one)
        kid = flush(kid, i, j)
        if kid not in pieces:
            dropped[kid] = dropped.get(kid, 0) + 1
            return
        m = mount(kid, pieces)
        if pal is None:
            kind = pieces[kid].get("kind")
            if kind in ("wall", "edge", "corner", "passage", "slab", "crown", "roof"):
                pal = house_palette(L, civ, i, j, lv - 1 if kind in ("edge", "roof", "crown") else lv)
            else:
                pal = civ.base_palette
        if kit_rot is None:
            kit_rot = (rot + 1) & 3 if kid in ACROSS else (rot + 2) & 3
        if flags & 4 and (i, j) in getattr(L, "q", {}):
            # (a piece standing on the ground: on the graded surface, not the raw deck)
            qq = L.q[(i, j)]
            lv, flags = qq // 4, (flags & ~4) | ((qq % 4) << 4)
        out.append((kid, i, j, lv, kit_rot, flags & 60, m, pal, ep))

    # pitched roof runs (the civ's choice per house): ridge along the house's longer side at that level; a run
    # segment where the run continues, the end piece (gable wall closing its -Z) at each end
    roofs = set((r[1], r[2], r[3]) for r in recs if r[0] in ("roof_terrace", "roof_tile", "roof_tin"))
    pitched = {}
    if hasattr(civ, "pitched"):
        groups = {}
        for (i, j, lv) in roofs:
            lid = int(L.lot[i, j])
            if lid >= 0:
                groups.setdefault((lid, lv), []).append((i, j))
        for (lid, lv), cs in groups.items():
            pr = civ.pitched(L, L.lots[lid], lv)
            if not pr:
                continue
            run, end = pr
            ii = [c[0] for c in cs]
            jj = [c[1] for c in cs]
            d = (0, 1) if (max(jj) - min(jj)) >= (max(ii) - min(ii)) else (1, 0)
            cset = set(cs)
            for (i, j) in cs:
                nxt = (i + d[0], j + d[1]) in cset
                prv = (i - d[0], j - d[1]) in cset
                fwd = 0 if d == (0, 1) else 1                       # kit rot turning +Z along d
                if nxt and prv:
                    pitched[(i, j, lv)] = (run, fwd)
                elif nxt:
                    pitched[(i, j, lv)] = (end, fwd)                # (its -Z gable faces back, the run goes on +Z)
                elif prv:
                    pitched[(i, j, lv)] = (end, (fwd + 2) & 3)
                else:
                    pitched[(i, j, lv)] = (end if end in pieces else run, fwd)
    L.pitched = pitched
    from lattice import WALKABLE

    def sloped(i, j):
        g = float(L.ground[i, j])
        # (any neighbour lower than this cell: the skirt closes the drop, KIT's rule)
        return any(L.inb(i + a, j + b) and float(L.ground[i + a, j + b]) < g - 0.08
                   for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))

    for (pid, i, j, lv, rot, flags, var, slot, ep) in recs:
        if pid in ("roof_terrace", "roof_tile", "roof_tin") and hasattr(civ, "roof_piece"):
            rp = civ.roof_piece(L, i, j, lv)
            if rp:
                put(rp[0], i, j, lv, 0, 0, ep, kit_rot=rp[1])
                continue
        if (i, j, lv) in pitched:
            if pid in ("roof_terrace", "roof_tile", "roof_tin"):
                kid, kr = pitched[(i, j, lv)]
                put(kid, i, j, lv, 0, 0, ep, kit_rot=kr)
                ge = getattr(civ, "gable_end_piece", None)
                if ge and kid.endswith("_end"):
                    put(ge, i, j, lv, 0, 0, ep, kit_rot=(kr + 2) & 3)   # (the firewall gable on the run's end)
                continue
            if pid.startswith("parapet") or pid.startswith("edge_eave") or pid == "edge_rail":
                continue                                        # (no parapet round a pitched roof)
        if pid.startswith("pave_") and flags & 4 and pid + "_skirt" in pieces and sloped(i, j):
            put(pid + "_skirt", i, j, lv, rot, flags, ep)       # (a sloping street: the skirt closes the step)
            continue
        if pid == "minaret_square":
            put("minaret_base" if lv == mina_low[(i, j)] else "minaret_shaft", i, j, lv, rot, flags, ep)
            continue
        if pid == "soffit" and L.lift[i, j] and lv == int(L.gk[i, j]) + int(L.lift[i, j]):
            put(getattr(civ, "SPEC", {}).get("stilt_piece", "floor_slab"), i, j, lv, rot, flags, ep)
            continue
        if pid == "soffit" and L.plan[i, j] in (LANE, ARTERY):
            # a room bridging a lane: the medina's sabat beams, Kowloon's alley ceiling (pipes, tubes, grime)
            cc = getattr(civ, "covered_ceiling", None) or ("sabat_beams" if medina else "alley_ceiling")
            if cc == "alley_ceiling" and h01(L.seed, "ceil", i, j) >= 0.34:
                cc = "floor_slab"
            put(cc, i, j, lv, rot, flags, ep)
            continue
        if pid == "arch_mouth":
            am = getattr(civ, "arch_mouth", "wall_arch_horseshoe" if medina else None)
            if not am:
                continue                                # (Kowloon: the alley ceiling is the mouth)
            pid = am
        kid = kit_id(pid, var, civ.id, pieces)
        if kid is None and pid.endswith("_skirt"):
            kid = kit_id(pid[:-6], var, civ.id, pieces)        # (a civ paving with no skirted twin: the plain one)
        if kid is None:
            dropped[pid] = dropped.get(pid, 0) + 1
            continue
        if kid in pieces and (i, j, lv) in shack_at and pieces[kid].get("kind") in ("overlay", "decor"):
            continue                                    # (a roof hut stands here: no dish or aerial inside it)
        put(kid, i, j, lv, rot, flags, ep)
        ce = getattr(civ, "SPEC", {}).get("corner_extra")
        if ce and pieces[kid].get("kind") == "corner" and lv == int(L.gk[i, j]) and h01(L.seed, "ce", i, j, rot) < ce[1]:
            put(ce[0], i, j, lv, rot, flags, ep)            # (a saint's niche on a street corner)
        if kid.startswith("edge_parapet") and hasattr(civ, "edge_extra"):
            for x in civ.edge_extra():                      # (e.g. the medina's white gypsum line under every roof edge)
                put(x, i, j, lv, rot, flags, ep)
        if pid in ("roof_terrace", "roof_tile", "roof_tin") and hasattr(civ, "roof_extra") and (i, j, lv) not in pitched:
            for x in civ.roof_extra(L, i, j, lv):           # crowns: pitched-roof stand-ins, domes, sacred hips
                put(x, i, j, lv, 0, 0, ep)
    # the newest roof huts (E5): the kit's tin shacks on the roof they stand on
    for (i, j, k) in shacks:
        sp = getattr(civ, "shack_pieces", ("ov_shack_a", "ov_shack_b", "ov_shack_c"))
        kid = sp[int(h01(L.seed, "shack", i, j) * len(sp))]
        put(kid, i, j, k, 0, 0, 5, pal=civ.lot_palette(L.lots[L.lot[i, j]]) if L.lot[i, j] >= 0 else civ.base_palette,
            kit_rot=int(h01(L.seed, "shr", i, j) * 4))
    # (one piece once: the same piece at the same place, turn and mount twice is a z-fight and a double collider)
    seen, uniq = set(), []
    for r in out:
        key = r[:7] if r[0] != "bridge_plank" else r[:4] + r[5:7]   # (two planks crossing in one cell: one)
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    L.dup_removed = len(out) - len(uniq)
    return uniq, dropped


# the night: every lamp the kit pieces carry, for the runtime's flares and light pools -- (kind, mount offset: across,
# up, out of the mount point)
LIGHTS = {"ov_lantern": ("lantern", 0.0, -0.55, 0.5), "ov_fluoro": ("fluoro", 0.0, 0.0, 0.06),
          "ov_festoon": ("festoon", 0.0, 2.7, 0.0), "int_lamp": ("lamp", 0.0, 2.6, 0.0),
          "minaret_top": ("minaret", 0.0, 3.2, 0.0), "wall_shopfront_a_t": ("shop", 0.0, 2.1, 0.45),
          "wall_shopfront_a_k": ("shop", 0.0, 2.1, 0.45), "wall_shopfront_b_t": ("shop", 0.0, 2.1, 0.45),
          "wall_shopfront_b_k": ("shop", 0.0, 2.1, 0.45), "wall_door_portal_k": ("door", 0.0, 2.9, 0.35),
          "wall_door_t": ("door", 0.0, 2.5, 0.3), "wall_door_k": ("door", 0.0, 2.5, 0.3),
          "ov_stall": ("stall", 0.0, 2.2, 0.0), "fountain_riad": ("fountain", 0.0, 1.0, 0.0)}
DIR = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}


def lights(L, civ, recs, kit):
    """[[x, y, z, kind, "#rrggbb"]] in the island frame (doors: about half lit)"""
    from pick import h01
    pal = kit["palettes"].get(civ.id) or [{}]
    out = []
    for (kid, i, j, lv, rot, flags, mnt, pv, ep) in recs:
        if kid not in LIGHTS:
            continue
        kind, ax, ay, az = LIGHTS[kid]
        if kind == "door" and h01(L.seed, "doorlamp", i, j, rot) > 0.5:
            continue
        x, _, z = L.centre(i, j)
        y = L.deck_y(x, z) if flags & 4 else lv * 3.2 + ((flags >> 4) & 3) * 0.8
        dx, dz = DIR[rot]
        out_d = az + (1.5 if mnt == 1 else 0.0)
        x += dx * out_d
        z += dz * out_d
        col = pal[pv % len(pal)].get("emissive", "#ffd890")
        out.append([round(x, 2), round(y + ay, 2), round(z, 2), kind, col])
    # tower tops: a lamp on a share of the high roofs (tower houses, the tallest blocks), seen from afar at night
    for (i, j, k) in getattr(L, "roof_cells", ()):
        if k - int(L.gk[i, j]) >= 6 and h01(L.seed, "towerlamp", i, j) < 0.25:
            x, _, z = L.centre(i, j)
            out.append([round(x, 2), round(k * 3.2 + 0.6, 2), round(z, 2), "tower", pal[civ.base_palette % len(pal)].get("emissive", "#ffd890")])
    return out


# the per-chunk budget (r4 §7: a LOD0 chunk <= 25k triangles): over it, the chunk sheds detail in this order --
# roof clutter and wall boxes, furniture, then the heavy openings step down to plainer bays (upper storeys first)
SHED = [
    ("drop", ("ov_antennas", "ov_pipe_run", "ov_ac", "ov_cables", "ov_dish", "ov_laundry", "ov_planter",
              "ov_rebar_stubs", "utility_pole", "ov_vending_machine")),
    ("drop", ("int_shelves", "int_table_set", "int_bed", "band_brick_relief", "ov_chochin_string")),
    ("swap", {"wall_balcony_cage_t": "wall_window_s_t", "wall_window_pair_t": "wall_window_s_t",
              "wall_window_pair_k": "wall_window_s_k", "wall_qamariya_k": "wall_window_s_k",
              "wall_screen_k": "wall_window_s_k", "wall_screen_t": "wall_window_s_t",
              "wall_balcony_timber_k": "wall_window_m_k", "wall_balcony_timber_t": "wall_window_m_t",
              "wall_balcony_iron_k": "wall_window_m_k", "wall_balcony_iron_t": "wall_window_m_t",
              "wall_bay_box_k": "wall_window_m_k", "wall_bay_box_t": "wall_window_m_t",
              "alley_ceiling": "floor_slab", "pave_court": "pave_plaza", "edge_eave_tile_green": "edge_parapet_plain_k",
              "edge_parapet_jali_k": "edge_parapet_plain_k", "wall_zellij_k": "wall_plain_k",
              "edge_parapet_rounded_k": "edge_parapet_plain_k", "edge_parapet_crenel_k": "edge_parapet_plain_k",
              "wall_gypsum_window_k": "wall_window_s_k", "wall_noren_t": "wall_shopfront_b_t",
              "wall_door_portal_k": "wall_door_k", "wall_cholet_front_t": "wall_window_l_t",
              "edge_eave_pagoda": "edge_eave_tin", "wall_roshan_t": "wall_roshan_lite_t", "wall_roshan_k": "wall_roshan_lite_k", "wall_jetty_t": "wall_jetty_lite_t",
              "wall_balcony_covered_k": "wall_balcony_timber_k", "wall_reja_box_k": "wall_window_s_k",
              "edge_parapet_urns_k": "edge_parapet_plain_k", "edge_cornice_pressed": "edge_parapet_plain_k",
              "ov_blue_pots": "ov_planter", "wall_window_medio_punto_k": "wall_window_l_k",
              "wall_tbilisi_balcony_t": "wall_balcony_timber_t", "wall_newar_window_k": "wall_window_m_k",
              "wall_newar_sanjhya_k": "wall_window_m_k", "wall_bay_box_k": "wall_window_m_k",
              "wall_bay_box_t": "wall_window_m_t", "wall_door_carved_k": "wall_door_k",
              "wall_inca_base_k": "wall_plain_k", "wall_inca_door_k": "wall_door_k", "wall_box_balcony_k": "wall_window_m_k",
              "wall_koshi_t": "wall_screen_t", "wall_luiken_k": "wall_window_m_k", "wall_gallery_timber_t": "wall_window_m_t",
              "wall_yemeni_mafraj_k": "wall_qamariya_k", "edge_parapet_crenel_white_k": "edge_parapet_plain_k"}),
    ("drop", ("wall_sign_column_t", "ov_sign_vertical_stack", "ov_sign_arm_big", "ov_roller_shutter", "ov_snow_cap",
              "band_zocalo", "dukkana_bench", "hoist_beam", "ov_toldo")),
    ("swap", {"wall_roshan_lite_t": "wall_window_m_t", "wall_roshan_lite_k": "wall_window_m_k",
              "wall_jetty_lite_t": "wall_window_m_t", "bell_tower_baroque_belfry": "bell_tower_baroque_base",
              "tower_mudejar_belfry": "tower_mudejar_shaft", "stair_plex_outdoor": "stair_spiral",
              "wall_mosaic_t": "wall_window_s_t", "wall_window_casement_pair_t": "wall_window_s_t",
              "wall_tile_t": "wall_window_s_t", "wall_verandah_t": "wall_window_s_t", "wall_brick_raw_t": "wall_plain_t",
              "wall_mural_t": "wall_plain_t", "wall_tin_corrugated_t": "wall_plain_t", "wall_qilou_t": "wall_shopfront_b_t",
              "wall_window_casement_k": "wall_window_s_k", "wall_triangles_k": "wall_door_k",
              "wall_door_studded_k": "wall_door_k", "wall_door_carriage_k": "wall_door_k",
              "wall_mashrabiya_box_k": "wall_screen_k", "wall_jharokha_k": "wall_window_m_k",
              "wall_jharokha_bangla_k": "wall_window_m_k", "wall_jharokha_canted_k": "wall_window_m_k",
              "wall_jali_carved_k": "wall_screen_k", "wall_veranda_gothic_t": "wall_window_m_t",
              "wall_cusped_arch_k": "wall_arch_pointed_k", "edge_parapet_date_plaque": "edge_parapet_plain_t",
              "edge_mangour_k": "edge_parapet_plain_k", "wall_ablaq_portal_k": "wall_door_k",
              "wall_portal_knockers_k": "wall_door_k", "wall_door_omani_k": "wall_door_k",
              "wall_orsi_k": "wall_window_m_k", "wall_kowloon_stack_t": "wall_balcony_cage_t",
              "roof_tile_hip_struts": "roof_terrace", "roof_thai_gable": "roof_terrace",
              "wall_tbilisi_balcony_t": "wall_tbilisi_balcony_lite_t", "wall_capiz_t": "wall_window_m_t",
              "wall_gallarija_k": "wall_balcony_timber_k", "wall_azulejo_k": "wall_balcony_iron_k",
              "wall_shushabandi_t": "wall_window_m_t", "wall_window_band_k": "wall_window_pair_k",
              "wall_triple_arch_loggia_k": "wall_arch_pointed_k", "wall_casement_louvre_t": "wall_window_pair_t",
              "wall_window_trapezoid_k": "wall_window_m_k", "wall_cumba_t": "wall_window_m_t",
              "wall_french_door_balcony_t": "wall_balcony_iron_t", "wall_carved_frame_k": "wall_window_s_k",
              "wall_kafes_t": "wall_window_pair_t", "wall_five_foot_way_t": "wall_shopfront_b_t",
              "abbara_vault": "floor_slab", "crown_spire": "green_hip", "tower_kasbah_corner_top": "minaret_base",
              "edge_parapet_pinnacle_k": "edge_parapet_plain_k", "wall_beam_ends_k": "wall_plain_k",
              "wall_earth_relief_k": "wall_plain_k"}),
    ("drop", ("ov_truck_art_panel", "ov_wedding_curtain", "ov_wire_net", "edge_chhajja", "ov_marigold_garland",
              "band_flood", "ov_mastaba", "ov_suq_canopy", "ov_prayer_flags", "roshan_crest", "ov_tank_drum",
              "pigeon_cote", "malqaf_scoop", "ov_arish_shade", "stupa", "tram_rail", "ov_jeepney", "ov_jangdok_jars",
              "chimney_stone", "ov_machicolation", "stair_external_white", "roof_dormer_attic", "miradouro_kiosk",
              "chimney_stack_pots", "lemon_pergola", "ov_wall_shrine", "band_damp", "band_peranakan_tile",
              "ov_gold_shop_neon", "ov_laundry_line_lane", "edge_pembe_frieze", "ov_prayer_flag_pole", "ov_roof_shrine",
              "corner_statue_niche", "cesme_fountain", "ov_wire_tangle")),
    ("drop", ("int_ceiling", "int_counter", "int_floor", "ov_tank", "ov_tank_round_blue", "ov_water_tower_steel")),
    ("swap", {"wall_window_pair_k": "wall_window_s_k", "wall_window_pair_t": "wall_window_s_t",
              "wall_balcony_timber_k": "wall_window_m_k", "wall_balcony_timber_t": "wall_window_m_t",
              "wall_balcony_iron_k": "wall_window_m_k", "wall_balcony_iron_t": "wall_window_m_t",
              "tulou_gallery_ring": "wall_window_m_t", "corner_quoin_k": "corner_chamfer_k",
              "corner_quoin_t": "corner_chamfer_k", "wall_window_m_k": "wall_window_s_k", "wall_window_m_t": "wall_window_s_t"}),
    ("drop", ("crown_band", "int_lamp", "green_hip", "plinth_t", "plinth_k")),
    ("swap", {"stilt_frame": "floor_slab", "dome_cap": "green_hip", "roof_pagoda": "green_hip"}),
    ("drop", ("edge_gable_step", "edge_gable_neck", "edge_gable_bell")),
    ("swap", {"wall_window_grille_t": "wall_plain_t", "wall_window_m_k": "wall_window_s_k",
              "wall_window_m_t": "wall_window_s_t", "wall_arch_horseshoe_k": "wall_blind_arch_k"}),
    ("swap", {"wall_window_s_t": "wall_plain_t", "wall_window_s_k": "wall_plain_k",
              "wall_blind_arch_k": "wall_plain_k"}),
]


def budget(L, recs, kit, limit=25000, chunk=8):
    """shed detail in the chunks over `limit` estimated triangles; returns the records and a {chunk: before} log"""
    from pick import h01
    pieces = kit["pieces"]
    tri = lambda kid: int(pieces[kid].get("tris", 100))
    by = {}
    for n, r in enumerate(recs):
        by.setdefault((r[1] // chunk, r[2] // chunk), []).append(n)
    recs = list(recs)
    gone = set()
    log = {}
    for key, ns in by.items():
        total = sum(tri(recs[n][0]) for n in ns)
        if total <= limit:
            continue
        log["%d,%d" % key] = total
        for how, what in SHED:
            if total <= limit:
                break
            cand = [n for n in ns if n not in gone and recs[n][0] in what]
            cand.sort(key=lambda n: (-recs[n][3], h01(L.seed, "shed", recs[n][1], recs[n][2], recs[n][3], recs[n][4])))
            for n in cand:
                if total <= limit:
                    break
                kid = recs[n][0]
                if how == "drop":
                    gone.add(n)
                    total -= tri(kid)
                else:
                    new = what[kid]
                    if new not in pieces:
                        continue
                    total -= tri(kid) - tri(new)
                    recs[n] = (new,) + tuple(recs[n][1:])
        if total > limit:
            # (still over: the heaviest decoration of any kind goes, the walls and the ground stay)
            cand = [n for n in ns if n not in gone and pieces[recs[n][0]].get("kind") in ("overlay", "decor", "sign", "crown")]
            cand.sort(key=lambda n: (-tri(recs[n][0]), h01(L.seed, "shed2", recs[n][1], recs[n][2], recs[n][3])))
            for n in cand:
                if total <= limit:
                    break
                gone.add(n)
                total -= tri(recs[n][0])
        if total > limit:
            # (and then: interiors go, the richest walls turn plain)
            cand = [n for n in ns if n not in gone and pieces[recs[n][0]].get("kind") in ("interior", "wall")]
            cand.sort(key=lambda n: (-tri(recs[n][0]), h01(L.seed, "shed3", recs[n][1], recs[n][2], recs[n][3])))
            for n in cand:
                if total <= limit:
                    break
                kid = recs[n][0]
                if pieces[kid].get("kind") == "interior":
                    gone.add(n)
                    total -= tri(kid)
                    continue
                plain = "wall_plain_t" if kid.endswith("_t") else "wall_plain_k"
                if plain in pieces and plain != kid and tri(plain) < tri(kid) and "door" not in kid:
                    total -= tri(kid) - tri(plain)
                    recs[n] = (plain,) + tuple(recs[n][1:])
    return [r for n, r in enumerate(recs) if n not in gone], log
