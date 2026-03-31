# ----------------------------------------------------------------------------
# preview.py
#
# For each generated H5 file in an input folder, generate a PNG figure with
# two columns: left = fake, right = ground-truth. Rows show slices sampled
# every 10 slices along the depth axis.
# Uses pathlib.Path for path handling and creates parent dirs as needed.
# ----------------------------------------------------------------------------

import argparse
from pathlib import Path
import h5py
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


def process_h5(h5_path: Path, out_dir: Path, step: int = 10):
    try:
        with h5py.File(str(h5_path), "r") as hf:
            # Expect datasets named 'fake' and 'gt'
            if "fake" not in hf or "gt" not in hf:
                print(f"Skipping {h5_path.name}: missing 'fake' or 'gt' datasets")
                return

            fake = np.array(hf["fake"]).astype(np.float32)
            gt = np.array(hf["gt"]).astype(np.float32)

    except Exception as e:
        print(f"Failed to read {h5_path}: {e}")
        return

    # Normalize shapes: expect (D, H, W) or (H, W) for single slice
    if fake.ndim == 3:
        # expected shape (D, H, W)
        pass
    elif fake.ndim == 2:
        # single 2D slice -> add depth axis
        fake = fake[np.newaxis, ...]
    else:
        print(f"Unsupported fake shape {fake.shape} in {h5_path}")
        return

    if gt.ndim == 3:
        pass
    elif gt.ndim == 2:
        gt = gt[np.newaxis, ...]
    else:
        print(f"Unsupported gt shape {gt.shape} in {h5_path}")
        return

    if fake.shape != gt.shape:
        print(f"Shape mismatch in {h5_path}: fake {fake.shape} vs gt {gt.shape}")
        # Try to broadcast if possible, otherwise skip
        min_depth = min(fake.shape[0], gt.shape[0])
        fake = fake[:min_depth]
        gt = gt[:min_depth]

    indices = list(range(0, fake.shape[0], step))
    if len(indices) == 0:
        indices = [0]

    nrows = len(indices)
    figsize = (8, 3 * nrows)

    fig, axes = plt.subplots(nrows=nrows, ncols=2, figsize=figsize)
    # Ensure axes is 2D array
    if nrows == 1:
        axes = np.expand_dims(axes, axis=0)

    for row_i, z in enumerate(indices):
        fake_slice = fake[z]
        gt_slice = gt[z]

        # compute display range from combined slices for fair comparison
        vmin = min(np.nanmin(fake_slice), np.nanmin(gt_slice))
        vmax = max(np.nanmax(fake_slice), np.nanmax(gt_slice))

        ax_fake = axes[row_i, 0]
        ax_gt = axes[row_i, 1]

        ax_fake.imshow(
            fake_slice, cmap="gray", vmin=vmin, vmax=vmax, interpolation="nearest"
        )
        ax_fake.set_title(f"Fake  slice {z}")
        ax_fake.axis("off")

        ax_gt.imshow(
            gt_slice, cmap="gray", vmin=vmin, vmax=vmax, interpolation="nearest"
        )
        ax_gt.set_title(f"GT    slice {z}")
        ax_gt.axis("off")

        # draw a horizontal center line on both images for visual reference
        h = fake_slice.shape[0]
        ax_fake.axhline(h // 2, color="r", linewidth=0.5)
        ax_gt.axhline(h // 2, color="r", linewidth=0.5)

    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (h5_path.stem + ".png")
    try:
        fig.savefig(str(out_path), dpi=150)
    except Exception as e:
        print(f"Failed to save figure for {h5_path}: {e}")
    finally:
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Preview .h5 fake vs gt slices")
    parser.add_argument("input_dir", type=str, help="Input folder containing .h5 files")
    parser.add_argument("output_dir", type=str, help="Output folder for PNG previews")
    parser.add_argument("--step", type=int, default=10, help="Slice step (default: 10)")
    parser.add_argument(
        "--recursive", action="store_true", help="Search input folder recursively"
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        print(f"Input folder does not exist: {input_dir}")
        return

    pattern = "**/*.h5" if args.recursive else "*.h5"
    h5_files = sorted(input_dir.glob(pattern))
    if not h5_files:
        print(f"No .h5 files found in {input_dir} (pattern={pattern})")
        return

    for h5_path in tqdm(h5_files, desc="Processing h5 files"):
        # preserve directory structure under output_dir
        rel = h5_path.relative_to(input_dir)
        out_subdir = output_dir / rel.parent
        process_h5(h5_path, out_subdir, step=args.step)


if __name__ == "__main__":
    main()