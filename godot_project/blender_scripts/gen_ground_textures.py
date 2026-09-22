#!/usr/bin/env python3
"""Generates tileable ground textures via numpy FFT low-pass noise (the
established technique for this project's seamless textures -- filtering
white noise in the FREQUENCY domain rather than blurring in image space,
since an FFT filter on an NxN grid is inherently circular/seamless; see
reference/memory.txt's gen_textures.py note). Pure PIL/numpy, no Blender.

Run: python3 blender_scripts/gen_ground_textures.py
Writes: assets/textures/gravel_tinted.png
"""

import numpy as np
from PIL import Image

OUT_DIR = "assets/textures"


def seamless_noise(size, cutoff, seed):
    """White noise, low-pass filtered in the frequency domain (a circular
    mask keeping only the lowest `cutoff` fraction of frequencies) --
    always tiles perfectly at `size`x`size` since FFT itself is periodic."""
    rng = np.random.default_rng(seed)
    white = rng.random((size, size))
    freq = np.fft.fft2(white)
    freq = np.fft.fftshift(freq)

    yy, xx = np.mgrid[0:size, 0:size]
    center = size / 2.0
    dist = np.sqrt((xx - center) ** 2 + (yy - center) ** 2) / center
    mask = (dist < cutoff).astype(np.float64)

    filtered = freq * mask
    filtered = np.fft.ifftshift(filtered)
    result = np.real(np.fft.ifft2(filtered))
    result -= result.min()
    if result.max() > 0:
        result /= result.max()
    return result


def gen_gravel(size=256):
    """Alley gravel: coarse blotchy base (stone clumps) + fine per-pixel
    speckle on top, in muted gray-brown gravel tones -- same two-layer
    "coarse blotch + sharp speckle" composition reference/memory.txt
    documents for other stone-ish textures in this project."""
    coarse = seamless_noise(size, cutoff=0.06, seed=4001)
    fine = seamless_noise(size, cutoff=0.35, seed=4002)
    speckle = np.random.default_rng(4003).random((size, size))

    base = coarse * 0.55 + fine * 0.30 + speckle * 0.15

    # Gray-brown gravel palette: low saturation, mid-low value.
    low = np.array([0.36, 0.33, 0.29])
    high = np.array([0.62, 0.58, 0.52])
    rgb = low[None, None, :] + (high - low)[None, None, :] * base[:, :, None]

    # Occasional darker pebbles -- a sparser, sharper speckle threshold
    # punched into the base color, not just a smooth gradient.
    pebble_mask = speckle > 0.93
    rgb[pebble_mask] *= 0.6

    img = (np.clip(rgb, 0.0, 1.0) * 255).astype(np.uint8)
    Image.fromarray(img, mode="RGB").save(f"{OUT_DIR}/gravel_tinted.png")
    print(f"wrote {OUT_DIR}/gravel_tinted.png ({size}x{size})")


if __name__ == "__main__":
    import os

    os.makedirs(OUT_DIR, exist_ok=True)
    gen_gravel()
