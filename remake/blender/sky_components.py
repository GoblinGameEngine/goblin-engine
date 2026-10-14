"""sky_components -- the sky islands' shared building components (remake/blender/sky/components/).

    import sky_components as SC
    SC.place(b, part, cid, frame, size=None, variant=None, mat=None, palette=None, **kw)
    SC.panel(b, style_id, kind, frame, bay_w, storey_h, **kw)
    SC.ceiling(b, part, rect, z, variant)
    SC.catalogue()

A shim: the package lives in remake/blender/sky/components, loaded under the name "skycomp" by path (a module
"sky" can't be relied on: gen/ may hold a generator called sky.py, which would shadow a package of that name).
See research/sky_islands/architecture/00_brief.md, "Round-2 build contract".
"""
import importlib.util
import os
import sys

_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sky", "components")
if "skycomp" not in sys.modules:
    _spec = importlib.util.spec_from_file_location("skycomp", os.path.join(_D, "__init__.py"), submodule_search_locations=[_D])
    _m = importlib.util.module_from_spec(_spec)
    sys.modules["skycomp"] = _m
    _spec.loader.exec_module(_m)

from skycomp import place, panel, ceiling, catalogue, anchor, palette_of, recipe, FAMILIES, IDS  # noqa: E402,F401
