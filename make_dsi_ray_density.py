#!/usr/bin/env python3
import os
import sys
import glob
import numpy as np
import imageio.v2 as imageio
import matplotlib
matplotlib.use("Agg")  # headless backend (no display needed)
import matplotlib.pyplot as plt


def save_ray_density_png(npy_path):
    """Load one DSI .npy file and save a *_ray_density.png image."""
    vol = np.load(npy_path)  # expected shape (Z, H, W) or (H, W, Z)

    if vol.ndim != 3:
        raise ValueError(f"Expected 3D array in {npy_path}, got shape {vol.shape}")

    # Interpret as (Z, H, W) = (depth, height, width)
    if vol.shape[0] in [80, 100, 120]:  # typical dimZ
        Z, H, W = vol.shape
        dsi = vol
    else:
        # maybe (H, W, Z)
        H, W, Z = vol.shape
        dsi = np.transpose(vol, (2, 0, 1))
        Z, H, W = dsi.shape

    # Ray density: sum of responses along depth
    ray_density = dsi.sum(axis=0)  # (H, W)

    # Avoid all-zero images
    rd = ray_density.astype(np.float32)
    rd -= rd.min()
    if rd.max() > 0:
        rd /= rd.max()

    # Plot with nice colormap on white background
    base, _ = os.path.splitext(os.path.basename(npy_path))
    out_png = f"{base}_ray_density.png"

    fig, ax = plt.subplots(figsize=(W / 80.0, H / 80.0))  # scale a bit
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    im = ax.imshow(rd, cmap="viridis", origin="upper")
    ax.axis("off")
    plt.tight_layout(pad=0)

    fig.savefig(out_png, dpi=200, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    print(f"Saved ray density PNG: {out_png}")


def make_gif_from_pngs(pattern="dsi_fused_*_ray_density.png",
                       out_name="ray_density.gif",
                       fps=10):
    """Build a GIF from all PNGs matching pattern."""
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"No files matched pattern: {pattern}")
        return

    frames = []
    for f in files:
        print(f"Adding frame: {f}")
        img = imageio.imread(f)
        frames.append(img)

    duration = 1.0 / float(fps)
    imageio.mimsave(out_name, frames, duration=duration)
    print(f"Saved GIF: {out_name} ({len(frames)} frames, fps={fps})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 make_dsi_ray_density.py dsi_fused_0000.npy   # make PNG for one DSI")
        print("  python3 make_dsi_ray_density.py gif [fps]            # make GIF from *_ray_density.png")
        sys.exit(1)

    mode = sys.argv[1]

    # Mode 1: called with a single .npy file
    if mode.endswith(".npy"):
        npy_path = mode
        if not os.path.isfile(npy_path):
            print(f"File not found: {npy_path}")
            sys.exit(1)
        save_ray_density_png(npy_path)

    # Mode 2: build GIF from all *_ray_density.png
    elif mode == "gif":
        fps = 10
        if len(sys.argv) >= 3:
            fps = float(sys.argv[2])
        make_gif_from_pngs(fps=fps)

    else:
        print(f"Unknown mode or file type: {mode}")
        print("Usage:")
        print("  python3 make_dsi_ray_density.py dsi_fused_0000.npy")
        print("  python3 make_dsi_ray_density.py gif [fps]")
        sys.exit(1)
