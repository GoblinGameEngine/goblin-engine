import sys, json, base64, numpy as np, collections
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
import lods
iid = sys.argv[1]
side, civ, x0, z0, cell, nx, nz, ids, recs = lods.read_warren(iid)
isl = [i for i in json.load(open('/home/deck/goblin-engine/godot_project/remake/sky/islands.json'))['islands'] if i['id'] == iid][0]
H = isl['height']; g = np.frombuffer(base64.b64decode(H['data']), '<i2').reshape(H['nz'], H['nx']) * 0.01
def dy(x, z):
    fx = (x - H['x0']) / H['step']; fz = (z - H['z0']) / H['step']
    ix = min(max(int(np.floor(fx)), 0), H['nx'] - 2); iz = min(max(int(np.floor(fz)), 0), H['nz'] - 2)
    tx = min(max(fx - ix, 0), 1); tz = min(max(fz - iz, 0), 1)
    return (g[iz, ix] * (1 - tx) + g[iz, ix + 1] * tx) * (1 - tz) + (g[iz + 1, ix] * (1 - tx) + g[iz + 1, ix + 1] * tx) * tz
pj = json.load(open('/home/deck/goblin-engine/godot_project/remake/sky/warrens/pieces.json'))['pieces']
c = collections.Counter(); d_hist = []
for r in recs:
    pid = ids[r['p']]
    if pj.get(pid, {}).get('kind') != 'ground': continue
    fl = int(r['rf'])
    x = x0 + 3 * int(r['i']) + 1.5; z = z0 + 3 * int(r['j']) + 1.5
    y = dy(x, z) if fl & 4 else 3.2 * int(r['k']) + 0.8 * (fl >> 6)
    top = pj[pid]['bounds'][1][1]
    # the deck at the cell's 4 corners and centre vs the paving top
    ds = [dy(x + a, z + b) for a, b in ((0, 0), (-1.4, -1.4), (1.4, -1.4), (-1.4, 1.4), (1.4, 1.4))]
    gap = min(abs(y + top - d) for d in ds)
    above = max(ds) - (y + top)
    c['deck' if fl & 4 else 'graded'] += 1
    if gap < 0.02: c['within 2 cm of the deck somewhere'] += 1
    if above > 0.0: c['deck pokes above the paving'] += 1
print(iid, dict(c))
