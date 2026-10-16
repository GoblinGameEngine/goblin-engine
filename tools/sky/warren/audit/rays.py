"""rays.py -- an Embree ray caster over a triangle soup (embreex), with a numpy fallback-free API.

  R = Rays(tris)                      tris (T, 3, 3)
  t, prim, n = R.cast(o, d, tmax)     first hit per ray: distance (inf: none), triangle index (-1), unit normal
                                      facing the ray's origin (zeros: none)
  R.down(xz, y_top, depth)            vertical rays straight down: hit y (nan: none), prim, normal
"""
import numpy as np
from embreex import rtcore_scene as rtcs
from embreex.mesh_construction import TriangleMesh


class Rays:
    def __init__(self, tris):
        self.tris = np.ascontiguousarray(tris, np.float32)
        self.n = len(self.tris)
        self.scene = rtcs.EmbreeScene()
        if self.n:
            TriangleMesh(self.scene, self.tris)
        e1 = self.tris[:, 1] - self.tris[:, 0]
        e2 = self.tris[:, 2] - self.tris[:, 0]
        nn = np.cross(e1, e2)
        ln = np.linalg.norm(nn, axis=1)
        self.normal = nn / np.maximum(ln, 1e-12)[:, None]
        self.area = 0.5 * ln

    def cast(self, o, d, tmax):
        o = np.ascontiguousarray(np.asarray(o, np.float32).reshape(-1, 3))
        d = np.asarray(d, np.float32).reshape(-1, 3)
        ln = np.linalg.norm(d, axis=1)
        d = np.ascontiguousarray(d / np.maximum(ln, 1e-12)[:, None])
        tm = np.ascontiguousarray(np.broadcast_to(np.asarray(tmax, np.float32), (len(o),)).astype(np.float32))
        if not self.n or not len(o):
            return np.full(len(o), np.inf), np.full(len(o), -1, np.int64), np.zeros((len(o), 3))
        r = self.scene.run(o, d, dists=tm.copy(), output=1)
        prim = r["primID"].astype(np.int64)
        hit = prim >= 0
        t = np.where(hit, r["tfar"], np.inf).astype(np.float64)
        n = np.zeros((len(o), 3))
        if hit.any():
            nn = self.normal[prim[hit]].astype(np.float64)
            s = np.sign(np.einsum("ij,ij->i", nn, d[hit]))
            n[hit] = -nn * np.where(s == 0, 1, s)[:, None]
        return t, prim, n

    def down(self, xz, y_top, depth):
        xz = np.asarray(xz, float).reshape(-1, 2)
        o = np.stack([xz[:, 0], np.broadcast_to(y_top, (len(xz),)), xz[:, 1]], 1)
        d = np.tile([0.0, -1.0, 0.0], (len(xz), 1))
        t, prim, n = self.cast(o, d, depth)
        y = np.where(np.isfinite(t), o[:, 1] - t, np.nan)
        return y, prim, n

    def up(self, p, h):
        p = np.asarray(p, float).reshape(-1, 3)
        return self.cast(p, np.tile([0.0, 1.0, 0.0], (len(p), 1)), h)
