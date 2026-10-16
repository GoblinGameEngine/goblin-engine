"""palettes.py -- the market kit's palettes: {key: [variant, ...]}, each variant {slot: "#rrggbb"} (sRGB).  A placement
picks a key (pieces.json "palette" is the piece's default key) and a variant index; the runtime multiplies COLOR_0's
grey shade by the variant's colour for each slot.  Markets: the 07 colours (research/flea_markets/07_names_and_signage.md).
Islanders: `skein` is the default; a moored island's clan colours replace canvas_a / canvas_b / canvas_c (colors[0..2])
and lining (colors[0] at 55 % value)."""
BASE = {
    "wall": "#c9c2b0", "trim": "#e9e1cc", "frame": "#6b4a2f", "wood": "#8a5f3a", "roof": "#7d8288", "fabric": "#c8553d",
    "accent": "#2f6f9f", "accent2": "#e3b23c", "concrete": "#a9a59c", "ground": "#6e6a62", "paint": "#f2f0e6", "paint2": "#c8202a",
    "plant": "#5b7f3a", "rope": "#c7a46a", "dark": "#2b2b2e", "cream": "#efe6cf",
    "metal": "#8e9196", "steel": "#b4b9bd", "brass": "#c9a23a",
    "canvas_a": "#e94f64", "canvas_b": "#f6c94b", "canvas_c": "#3fb6c8", "lining": "#7a3fa0",
    "glass": "#2c3a42", "glow": "#ffd28a", "glow_b": "#bfe9ff",
    "bulb": "#ffd890", "bulb_a": "#ff5a5a", "bulb_b": "#5aff7a", "bulb_c": "#5ab0ff", "bulb_d": "#ffd23a", "neon": "#2bf0e0",
    "neon_b": "#ff4a9a", "lamp": "#fff1d6", "warn": "#ff2a1a",
    "sign": "#ffffff", "mascot": "#ffffff", "stall": "#ffffff", "goods": "#ffffff", "text": "#ffffff",
}


def P(**kw):
    d = dict(BASE)
    d.update(kw)
    return d


MARKET = {
    "fm01_ropewalk": P(wood="#7a5a3a", concrete="#6e6e6a", trim="#c9a23a", accent="#8e2b22", bulb="#ffc46a"),
    "fm02_lobster_pot": P(concrete="#7a7a74", wood="#8a6a4a", accent="#c8341f", accent2="#f2c230", cream="#f4f1e8"),
    "fm03_tide_clock": P(cream="#f4f4ef", roof="#1f2f55", trim="#d9d4c4", dark="#1f2f55", concrete="#8a8780"),
    "fm04_net_loft": P(wall="#8d9196", roof="#6e7277", wood="#9a5a4a", dark="#4a4d52", concrete="#7a7a74"),
    "fm05_water_tower": P(steel="#b8bcc0", metal="#c4c8cc", concrete="#8a8780"),
    "fm06_book_barn": P(cream="#f4f1e8", roof="#3a3d40", accent="#1f5a3a", accent2="#6a2a2a", wall="#8a3a2a"),
    "fm07_weathervane": P(wood="#6a4a30", concrete="#8a8780", brass="#4f9a7f", metal="#3a5a4a"),
    "fm08_brannock_trade_days": P(cream="#f4f4ef", brass="#d4af37", dark="#1f2f55", concrete="#8a8780"),
    "fm09_boathouse_swap": P(cream="#f4f4ef", accent="#1f5a3a", accent2="#2a7a46", metal="#4a4a4a"),
    "fm10_four_corners_swap": P(cream="#f4f4ef", trim="#f08a3c", dark="#2a2a2a"),
    "fm11_regatta_swap": P(cream="#f6f6f2", accent="#9ec9e8", accent2="#f2b6c6", fabric="#c8e6b0", metal="#c4c8cc"),
    "fm12_millwheel_market": P(wood="#8a6a42", concrete="#8d8a84", glow_b="#9fd6ff"),
    "fm13_traders_landing": P(dark="#1a1a1a", accent="#b8241c", trim="#f4f1e8", cream="#f4f1e8", metal="#2a2a2a"),
    "fm14_iron_wheel": P(cream="#efe6cf", accent="#2f7a5a", accent2="#1a1a1a", dark="#1a1a1c", steel="#c4c8cc", trim="#d8d0bc"),
    "fm15_red_granary": P(accent="#b8241c", roof="#5a5a5a", cream="#f4f4ef", accent2="#f2c230", concrete="#9a958c", bulb_a="#ffd890"),
    "fm16_tall_tamarack": P(plant="#d9a62e", accent="#c88a1e", wood="#6a4a30", metal="#2bb3b1"),
    "fm17_elevator_flea_days": P(concrete="#d8d4cc", cream="#e9e5dc", roof="#8a8a8a"),
    "fm18_route30_swap_meet": P(accent2="#2bb3b1", cream="#f4f4ef", trim="#f08a3c", bulb_a="#ffb43a"),
    "fm19_la_pulga_verde": P(cream="#e9d6a8", accent2="#c86a3a", roof="#b8502e", wood="#8a6a4a", plant="#3f8a3a"),
    "fm20_starlite_swap": P(accent2="#1b2a4a", accent="#f0803c", fabric="#e85a8c", trim="#2bb3b1", cream="#e9d6a8", dark="#1b2a4a", steel="#8a8f96"),
    "fm21_carousel_swap": P(accent="#e8344c", cream="#fff6e8", accent2="#5ab0e8", brass="#d4af37"),
    "fm22_pelican_swap": P(cream="#e9d6a8", wood="#8a6a4a"),
}

PALETTES = {k: [v] for k, v in MARKET.items()}
PALETTES.update({
    "north": [P(cream="#efe3c2", trim="#2f5d50", concrete="#6e6e6a", brass="#c9a23a", bulb="#ffc46a"),
              P(cream="#f4f1e8", trim="#8e2b22", concrete="#6e6e6a", brass="#c9a23a", bulb="#ffc46a")],
    "river": [P(wall="#8e4a32", trim="#d8c8a8", steel="#2f5d50", accent="#f08a3c"),
              P(wall="#7a3a2a", trim="#e9dfc4", steel="#3a4a6a", accent="#2bb3b1")],
    "south": [P(cream="#f2e4c8", accent="#2bb3b1", accent2="#f0803c", neon="#ff6a9a", bulb_a="#ffd23a"),
              P(cream="#f4ece0", accent="#e85a8c", accent2="#2bb3b1", neon="#2bf0e0", bulb_a="#ffb43a")],
    "shed": [P(wall="#8e2b22", trim="#efe3c2", roof="#5a5e62", cream="#efe3c2", steel="#8a8f96", wood="#7a5a3a"),
             P(wall="#e9dfc4", trim="#2f5d50", roof="#6a6e72", cream="#f4f1e8", steel="#8a8f96", wood="#7a5a3a"),
             P(wall="#b4b9bd", trim="#3a6a9a", roof="#a4a9ad", cream="#f4f1e8", steel="#9aa0a6", wood="#8a6a42")],
    "stall": [P(fabric="#c8553d", accent="#f4f1e8", accent2="#2f6f9f"), P(fabric="#2f6f9f", accent="#f4f1e8", accent2="#c8553d"),
              P(fabric="#3f8a3a", accent="#f2c230", accent2="#f4f1e8"), P(fabric="#e3b23c", accent="#c8553d", accent2="#2f6f9f"),
              P(fabric="#7a3fa0", accent="#f4f1e8", accent2="#e3b23c"), P(fabric="#f4f1e8", accent="#2bb3b1", accent2="#e85a8c")],
    "lot": [P(), P(paint="#f2c230")],
    "white": [P()],
    "skein": [P(), P(canvas_a="#2bb3b1", canvas_b="#ff7a3c", canvas_c="#f6e04b", lining="#1f4f8a", accent="#ff7a3c", accent2="#f6e04b"),
              P(canvas_a="#7a3fa0", canvas_b="#3fd08a", canvas_c="#ff5a8a", lining="#3a1f5a", accent="#3fd08a", accent2="#ff5a8a"),
              P(canvas_a="#f4f1e8", canvas_b="#2f6f9f", canvas_c="#e94f64", lining="#8a2a3a", accent="#2f6f9f", accent2="#e94f64")],
    "logistics": [P(canvas_a="#f4f4f0", canvas_b="#e8e8e2", canvas_c="#ff7a3c", lining="#d8d8d0", accent="#ff7a3c", accent2="#1f3b6e")],
    "ropeway": [P(accent="#e94f64", accent2="#f6c94b", steel="#c4c8cc", metal="#5a5f66", cream="#f4f1e8", dark="#24262a"),
                P(accent="#2bb3b1", accent2="#ff7a3c", steel="#c4c8cc", metal="#5a5f66", cream="#f4f1e8", dark="#24262a")],
    "mooring": [P(steel="#c8302a", metal="#5a5f66", concrete="#a9a59c", trim="#f4f1e8")],
    # the floating pier (MARKETS-WORLD, p_world.py): weathered decking on grey pontoons, white rails at the Regatta
    "pier": [P(wood="#9a7a56", frame="#5a4632", concrete="#8d9294", dark="#2b2b2e", rope="#d8c9a0", steel="#c4c8cc"),
             P(wood="#e9e4d8", frame="#5a4632", concrete="#8d9294", dark="#1f2f55", rope="#d8c9a0", steel="#c4c8cc")],
})
