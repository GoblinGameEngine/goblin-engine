#!/usr/bin/env python3
"""Generates cliff_rock.png -- the lower-wall texture (bottom 60% of
floor-to-ceiling, per shaders/wall_cliff_sky.gdshader; the top 40% blends
into the same sky as the ceiling). Same seamless FFT low-pass noise
technique as gen_ground_textures.py's gravel. The jagged mountain-top
silhouette itself is done in the SHADER (a noise-perturbed cliff/sky
blend threshold, not baked into this texture) -- this texture only needs
to tile cleanly along the U axis (tangential, all the way around the
ring) and read as rock from floor to the blend zone.

Run: python3 blender_scripts/gen_cliff_texture.py
Writes: assets/textures/cliff_rock.png
"""

import numpy as np
from PIL import Image

OUT_DIR = "assets/textures"


def seamless_noise(size, cutoff, seed):
    rng = np.random.default_rng(seed)
    white = rng.random((size, size))
    freq = np.fft.fftshift(np.fft.fft2(white))
    yy, xx = np.mgrid[0:size, 0:size]
    center = size / 2.0
    dist = np.sqrt((xx - center) ** 2 + (yy - center) ** 2) / center
    mask = (dist < cutoff).astype(np.float64)
    result = np.real(np.fft.ifft2(np.fft.ifftshift(freq * mask)))
    result -= result.min()
    if result.max() > 0:
        result /= result.max()
    return result


def gen_cliff(size=512):
    # Three noise layers: broad rock-face striation (elongated vertically
    # by stretching a low-cutoff field), coarse blotch (lichen/mineral
    # patches), fine per-pixel grain.
    coarse = seamless_noise(size, cutoff=0.05, seed=5001)
    mid = seamless_noise(size, cutoff=0.15, seed=5002)
    fine = seamless_noise(size, cutoff=0.4, seed=5003)

    base = coarse * 0.5 + mid * 0.35 + fine * 0.15

    # Vertical striation -- rock faces read as banded/layered strata far
    # more than a flat blotch pattern does; achieved by biasing brightness
    # with a second noise field stretched along Y (sampled every 3rd row).
    strata_src = seamless_noise(size, cutoff=0.08, seed=5004)
    strata = strata_src[:: max(1, size // 172), :]
    strata = np.repeat(strata, int(np.ceil(size / strata.shape[0])), axis=0)[:size, :]
    base = np.clip(base * 0.75 + strata * 0.25, 0.0, 1.0)

    # Gray-brown rock palette, darker in the low bands (base of a cliff
    # reads darker/damper than upper faces in most real rock).
    low = np.array([0.22, 0.20, 0.18])
    high = np.array([0.52, 0.47, 0.42])
    rgb = low[None, None, :] + (high - low)[None, None, :] * base[:, :, None]

    # Sparse dark cracks/fissures -- a harder-edged speckle than the
    # smooth strata, punched in as darker flecks.
    crack_mask = fine > 0.92
    rgb[crack_mask] *= 0.55

    img = (np.clip(rgb, 0.0, 1.0) * 255).astype(np.uint8)
    Image.fromarray(img, mode="RGB").save(f"{OUT_DIR}/cliff_rock.png")
    print(f"wrote {OUT_DIR}/cliff_rock.png ({size}x{size})")


if __name__ == "__main__":
    import os

    os.makedirs(OUT_DIR, exist_ok=True)
    gen_cliff()
