"""offline checks on the warren mooring pieces with the market kit's clip / pass / topology checks (built from source)"""
import sys, numpy as np
ROOT = '/home/deck/goblin-engine'
sys.path.insert(0, ROOT + '/remake/blender/sky/warren_kit'); sys.path.insert(0, ROOT + '/tools/sky/warren/audit')
sys.path.insert(0, ROOT + '/remake/blender/markets')
import pieces, pieces_moor as PM, flicker
import meshlib as M, rays as RY
import importlib.util
spec = importlib.util.spec_from_file_location("mcheck", ROOT + "/remake/blender/markets/check.py"); K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
SOFT = {"glass", "emissive", "fabric", "screen"}
for pid in ['moor_line_house', 'moor_station_pax', 'moor_station_cargo', 'moor_drop_cage_davit', 'moor_signal_mast']:
    m, log = flicker.finish(pid, pieces.PIECES[pid], pieces.PIECES[pid]['build']())
    tr, sl = [], []
    for s in m.tris:
        for t in m.tris[s]:
            tr.append(t[:3]); sl.append(s)
    tris = np.array(tr, float); sl = np.array(sl)
    t = M.topology(tris)
    comp = K.components(tris); R = RY.Rays(tris); closed = K.comp_closed(tris, comp)
    cross, joint = K.clipping(tris, comp, R)
    gs = {}
    for i, c in enumerate(comp): gs.setdefault(int(c), sl[i])
    vis = [c for c in cross if (not closed[c[1]]) or (not closed[c[2]]) or gs[c[1]] in SOFT or gs[c[2]] in SOFT]
    zf = M.coplanar_overlaps(tris, comp, min_area=2e-4)
    sp = PM.SPECIAL.get(pid, {})
    pb = []
    if 'pass' in sp:
        lo, hi = np.array(sp['pass'][0]), np.array(sp['pass'][1])
        ins = M.tri_box_overlap(tris, lo + 0.01, hi - 0.01)
        pb = tris[np.nonzero(ins)[0][:3]].mean(1).round(2).tolist() if ins.any() else []
        fb = [b for b in sp['frame'] if K.box_overlap((lo + 0.005, hi - 0.005), b)]
    else:
        fb = []
    print(pid, m.count(), 'nonman', t['nonmanifold_edges'], 'incons', t['inconsistent_edges'], 'inout', t['inside_out'], 'degen', t['degenerate'], 'dup', t['dup_faces'],
          'clips', len(vis), [c[0].round(2).tolist() for c in vis[:3]], 'zfight', len(zf), [z[3] for z in zf[:2]], 'pass_tris', len(pb), pb, 'pass_frames', fb[:2], 'cure', len(log))
