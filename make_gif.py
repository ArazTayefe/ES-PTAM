#!/usr/bin/env python3
"""
Combine a sequence of images (e.g., depth_0000.png, depth_0001.png, ...)
into an animated GIF.

Usage (inside the folder with your images):
    python make_gif.py --pattern "depth_*.png" --output depth_map.gif --fps 10
"""

import argparse
from pathlib import Path
import imageio.v2 as imageio  # imageio.v2 is the current stable interface
import sys


def make_gif(input_dir, pattern, output_path, fps):
    input_dir = Path(input_dir)
    output_path = Path(output_path)

    # Find files matching the pattern, e.g. depth_*.png
    frames = sorted(input_dir.glob(pattern))
    if not frames:
        print(f"[ERROR] No files found in {input_dir} matching pattern '{pattern}'")
        sys.exit(1)

    print(f"[INFO] Found {len(frames)} frames.")
    print(f"[INFO] First frame: {frames[0].name}")
    print(f"[INFO] Last  frame: {frames[-1].name}")

    # Duration in seconds per frame
    duration = 1.0 / fps

    images = []
    for f in frames:
        img = imageio.imread(f)
        images.append(img)

    print(f"[INFO] Writing GIF to {output_path} (fps={fps}, duration={duration:.3f}s per frame)...")
    imageio.mimsave(output_path, images, duration=duration)
    print("[INFO] Done.")


def main():
    parser = argparse.ArgumentParser(description="Create a GIF from a sequence of images.")
    parser.add_argument(
        "--input_dir",
        type=str,
        default=".",
        help="Directory containing input images (default: current directory)",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="depth_*.png",
        help="Glob pattern for input images (default: depth_*.png)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.gif",
        help="Output GIF filename (default: output.gif)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=10.0,
        help="Frames per second for the GIF (default: 10)",
    )

    args = parser.parse_args()
    make_gif(args.input_dir, args.pattern, args.output, args.fps)


if __name__ == "__main__":
    main()
