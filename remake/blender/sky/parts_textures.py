"""parts_textures.py -- the sky islands' snow textures (numpy + PIL; ssc-assets venv). Tileable: noise is shaped in
Fourier space, so it wraps exactly.

  ~/.venvs/ssc-assets/bin/python remake/blender/sky/parts_textures.py

  textures/snow_albedo.png    512 px RGB: packed snow, faint blue-grey drifts and grain
  textures/snow_coverage.png  256 px RGB: R low-frequency coverage field (snow lands where R < cover: patches grow
                              into a blanket as cover rises 0..1, and shrink back as it melts), G mid-frequency
                              breakup for the patch edges, B a sparse sparkle mask
"""
import os

import numpy as np
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "godot_project", "remake", "sky", "textures")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(20261014)


def noise(n, f0, f1, power=1.0):
    """tileable band-limited noise, frequencies f0..f1 cycles per tile, normalised to 0..1"""
    k = np.fft.fftfreq(n) * n
    kx, ky = np.meshgrid(k, k)
    r = np.sqrt(kx ** 2 + ky ** 2)
    amp = np.where((r >= f0) & (r <= f1), 1.0 / np.maximum(r, 1.0) ** power, 0.0)
    ph = np.exp(2j * np.pi * rng.random((n, n)))
    a = np.real(np.fft.ifft2(amp * ph))
    a -= a.min()
    return a / a.max()


def equalise(a):
    """rank-normalise to a uniform 0..1 distribution (so 'cover' maps linearly to the share of ground covered)"""
    flat = a.ravel()
    out = np.empty_like(flat)
    out[np.argsort(flat)] = np.linspace(0.0, 1.0, flat.size)
    return out.reshape(a.shape)


n = 512
drift = noise(n, 1, 6, 1.0)
grain = noise(n, 40, 200, 0.5)
v = 0.90 + 0.06 * drift + 0.03 * (grain - 0.5)
rgb = np.stack([v * 0.97, v * 0.985, v * 1.0], -1)
rgb[..., 0] -= 0.05 * (1 - drift)          # hollows a touch blue
rgb[..., 1] -= 0.025 * (1 - drift)
Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, "snow_albedo.png"), optimize=True)

m = 256
cov = equalise(noise(m, 1, 5, 1.2) * 0.8 + noise(m, 5, 12, 1.0) * 0.2)
brk = noise(m, 12, 40, 0.8)
spark = (rng.random((m, m)) > 0.985).astype(float) * (0.5 + 0.5 * rng.random((m, m)))
img = np.stack([cov, brk, spark], -1)
Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(OUT, "snow_coverage.png"), optimize=True)
print("wrote", OUT)
