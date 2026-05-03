# ------------------------------------------------------------------------------
# indiana_comparison_visuals.py
#
# Generates PDF and HTML comparison visualizations for CTGAN inference on the
# Indiana University chest X-ray dataset. For each patient, it runs inference
# with all 4 model variants (Original, Synthetic, Real, Mixed) and produces
# a combined comparison view. Each PDF page shows the input xrays and
# generated CT from all 4 variants side-by-side. HTML visualizations are
# saved in per-patient subdirectories.
# ------------------------------------------------------------------------------

import argparse
import copy
import json
import os
import pickle
from collections import defaultdict, OrderedDict
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm
from PIL import Image

# Add 3DGAN lib to path
script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(script_dir, "lib")
import sys

sys.path.insert(0, lib_path)

from lib.config.config import cfg_from_yaml, cfg, merge_dict_and_yaml, print_easy_dict
from lib.dataset.factory import get_dataset
from lib.model.factory import get_model
from lib.utils.visualizer import tensor_back_to_unnormalization

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Import the self-contained xray classifier
from lib.xray_classifier import classify_xray_view, _preprocess_array


# Model variants to iterate over (same as comparison_visuals.py)
MODEL_VARIANTS = [
    ("d2_multiview2500", "Model C"),
    ("multiview-GAN-dataset-complete-clipped-shifted", "Model E"),
    ("multiview-GAN-dataset-complete-clipped-shifted-real_mixed", "Model M"),
]


def load_classification_cache(cache_path):
    """Load classification cache from JSON file."""
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    return {}


def save_classification_to_cache(cache_path, image_path, view_type):
    """Save a single classification to the cache JSON file."""
    cache = load_classification_cache(cache_path)
    cache[str(image_path)] = view_type
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2)


def get_cached_or_classify(image_path, cache_path, classifier_weights, img_array):
    """Check cache for classification, classify if not found, and save to cache."""
    cache = load_classification_cache(cache_path)
    image_path_str = str(image_path)
    if image_path_str in cache:
        return cache[image_path_str]
    view_type = classify_xray_view(img_array, weights_path=classifier_weights)
    save_classification_to_cache(cache_path, image_path_str, view_type)
    return view_type


def parse_args():
    parse = argparse.ArgumentParser(description="CTGAN Indiana Comparison Visuals")
    parse.add_argument(
        "--indiana_dir",
        type=str,
        default="data/indiana_png",
        dest="indiana_dir",
        help="path to Indiana PNG dataset directory",
    )
    parse.add_argument(
        "--tag",
        type=str,
        default="indiana_comparison",
        dest="tag",
        help="distinct tag for output directory",
    )
    parse.add_argument(
        "--data", type=str, default="indiana", dest="data", help="input data identifier"
    )
    parse.add_argument(
        "--ymlpath", type=str, default=None, dest="ymlpath", help="config yaml path"
    )
    parse.add_argument(
        "--gpu", type=str, default="0,1", dest="gpuid", help="gpu is split by ,"
    )
    parse.add_argument(
        "--dataset_class",
        type=str,
        default="align_ct_xray_views_std",
        dest="dataset_class",
        help="Dataset class should select from unalign / align_ct_xray_views_std / etc.",
    )
    parse.add_argument(
        "--model_class",
        type=str,
        default="cyclegan",
        dest="model_class",
        help="Model class should select from cyclegan / ",
    )
    parse.add_argument(
        "--check_point",
        type=str,
        default=None,
        dest="check_point",
        help="which epoch to load? ",
    )
    parse.add_argument(
        "--latest",
        action="store_true",
        dest="latest",
        help="set to latest to use latest cached model",
    )
    parse.add_argument(
        "--verbose",
        action="store_true",
        dest="verbose",
        help="if specified, print more debugging information",
    )
    parse.add_argument(
        "--model_root",
        type=str,
        default=None,
        dest="model_root",
        help="Root path to model weights directory (contains variant subdirs)",
    )
    parse.add_argument(
        "--how_many",
        type=int,
        dest="how_many",
        default=50,
        help="if specified, only process this number of patients",
    )
    parse.add_argument(
        "--resultdir", type=str, default="", dest="resultdir", help="dir to save result"
    )
    parse.add_argument(
        "--classifier_weights",
        type=str,
        default="save_models/xray_classifier.pth",
        dest="classifier_weights",
        help="path to xray classifier weights",
    )
    parse.add_argument(
        "--cache",
        type=str,
        default="data/indiana_xray_classification_cache.json",
        dest="cache",
        help="path to classification cache JSON file",
    )
    args = parse.parse_args()
    return args


def group_images_by_patient(indiana_dir):
    """Group images by patient ID from the Indiana PNG dataset."""
    indiana_dir = Path(indiana_dir)
    files = sorted([f for f in os.listdir(indiana_dir) if f.endswith(".png")])

    groups = defaultdict(list)
    for f in files:
        # Extract patient ID from filename
        # Pattern: CXR{num}[_{suffix}]_IM-{id}-{viewcode}.png
        name_without_ext = f.replace(".png", "")
        parts = name_without_ext.split("_")

        if parts[0] == "CXR":
            # Handle CXR{num} or CXR{num}_{suffix} format
            if len(parts) >= 3 and parts[2] == "IM":
                # Format: CXR1_1_IM-0001-3001
                patient_id = "_".join(parts[:2])  # CXR1_1
            elif len(parts) >= 2 and parts[1].startswith("IM"):
                # Format: CXR1_IM-0001-3001 (rare)
                patient_id = parts[0]
            elif len(parts) >= 2 and not parts[1].startswith("IM"):
                # Format: CXR1_1_IM-0001-3001
                patient_id = "_".join(parts[:2])
            else:
                patient_id = parts[0]
        else:
            patient_id = parts[0]

        groups[patient_id].append(indiana_dir / f)

    return groups


def classify_and_pair_images(
    patient_groups, classifier_weights, cache_path, fine_size=128
):
    """
    Classify each image as frontal or lateral and pair them per patient.
    Uses JSON cache to avoid re-classifying images.
    Returns list of dicts: {'patient_id': str, 'frontal': PIL.Image, 'lateral': PIL.Image}
    """
    paired_samples = []

    for patient_id, image_paths in tqdm(
        patient_groups.items(), desc="Classifying views"
    ):
        if len(image_paths) < 2:
            # Skip patients with fewer than 2 images
            continue

        # Load all images for this patient
        patient_images = []
        for img_path in image_paths:
            try:
                img = Image.open(img_path).convert("L")  # Convert to grayscale
                # Resize to fine_size x fine_size
                img = img.resize((fine_size, fine_size), Image.LANCZOS)
                img_arr = np.array(img).astype(np.float32) / 255.0
                patient_images.append({"path": img_path, "array": img_arr})
            except Exception as e:
                print(f"Error loading {img_path}: {e}")
                continue

        if len(patient_images) < 2:
            continue

        # Classify each image (using cache)
        frontal_images = []
        lateral_images = []

        for img_data in patient_images:
            try:
                view_type = get_cached_or_classify(
                    img_data["path"], cache_path, classifier_weights, img_data["array"]
                )
                img_data["view"] = view_type
                if view_type == "frontal":
                    frontal_images.append(img_data)
                else:
                    lateral_images.append(img_data)
            except Exception as e:
                print(f"Error classifying {img_data['path']}: {e}")
                continue

        # Pair one frontal with one lateral if available
        if frontal_images and lateral_images:
            # Use the first available pair
            paired_samples.append(
                {
                    "patient_id": patient_id,
                    "frontal": frontal_images[0],
                    "lateral": lateral_images[0],
                }
            )
        elif len(frontal_images) >= 2:
            # Use two different frontal views as frontal/lateral substitute
            paired_samples.append(
                {
                    "patient_id": patient_id,
                    "frontal": frontal_images[0],
                    "lateral": frontal_images[1],
                    "note": "both_frontal",
                }
            )
        elif len(lateral_images) >= 2:
            paired_samples.append(
                {
                    "patient_id": patient_id,
                    "frontal": lateral_images[0],
                    "lateral": lateral_images[1],
                    "note": "both_lateral",
                }
            )

    return paired_samples


def normalize_for_display(img, vmin=None, vmax=None):
    """Normalize array to [0, 1] for display."""
    img = img.astype(np.float32)
    if vmin is None:
        vmin = np.nanmin(img)
    if vmax is None:
        vmax = np.nanmax(img)
    if vmax - vmin == 0:
        return np.zeros_like(img)
    return (img - vmin) / (vmax - vmin)


def run_inference_single(model_variant, model_root, patient_data, opt):
    """
    Loads model weights for a given variant and runs inference on a single patient.
    Model is loaded fresh on each call and unloaded when function returns.

    Args:
        model_variant: e.g. "d2_multiview2500"
        model_root: root path to model weights
        patient_data: dict with 'frontal' and 'lateral' arrays
        opt: pre-initialized config object

    Returns:
        sample: dict with 'name', 'fake', 'frontal', 'lateral', 'model_variant'
    """
    # Build load_path
    load_path = f"{model_root.rstrip('/')}/{model_variant}/checkpoint"

    # Override load_path - rest of config comes from pre-built opt
    opt_variant = copy.deepcopy(opt)
    opt_variant.load_path = load_path

    # Get model
    gan_model = get_model(opt_variant.model_class)()
    gan_model.eval()
    gan_model.init_process(opt_variant)
    gan_model.setup(opt_variant)

    # Set to test Mode again
    if "batch" in opt_variant.norm_G:
        gan_model.eval()
    elif "instance" in opt_variant.norm_G:
        gan_model.eval()
        for name, m in gan_model.named_modules():
            if m.__class__.__name__.startswith("InstanceNorm"):
                m.train()
    else:
        raise NotImplementedError()

    # Prepare input tensors
    frontal_arr = patient_data["frontal"]["array"]
    lateral_arr = patient_data["lateral"]["array"]

    # Create input dict for model
    # CT should be 4D (B, D, H, W) - shape (1, 128, 128, 128)
    ct_tensor = torch.zeros(1, 128, 128, 128)

    # Prepare xray tensors with proper normalization
    frontal_tensor = torch.from_numpy(frontal_arr).unsqueeze(0).unsqueeze(0)  # 1x1xHxW
    lateral_tensor = torch.from_numpy(lateral_arr).unsqueeze(0).unsqueeze(0)  # 1x1xHxW

    # Apply min-max normalization if specified in config
    if hasattr(opt_variant, "XRAY1_MIN_MAX") and opt_variant.XRAY1_MIN_MAX is not None:
        xmin, xmax = opt_variant.XRAY1_MIN_MAX
        if xmax != xmin:
            frontal_tensor = (frontal_tensor - xmin) / (xmax - xmin)

    if hasattr(opt_variant, "XRAY2_MIN_MAX") and opt_variant.XRAY2_MIN_MAX is not None:
        xmin, xmax = opt_variant.XRAY2_MIN_MAX
        if xmax != xmin:
            lateral_tensor = (lateral_tensor - xmin) / (xmax - xmin)

    # Clamp to [0, 1]
    frontal_tensor = torch.clamp(frontal_tensor, 0, 1)
    lateral_tensor = torch.clamp(lateral_tensor, 0, 1)

    xray_tuple = (frontal_tensor, lateral_tensor)

    # Create paths
    frontal_path = str(patient_data["frontal"]["path"])
    lateral_path = str(patient_data["lateral"]["path"])

    # Set input to model
    gan_model.set_input(
        (ct_tensor, (frontal_tensor, lateral_tensor), frontal_path, lateral_path)
    )

    # Run forward pass
    gan_model.test()

    # Get visuals
    visuals = gan_model.get_current_visuals()

    # Get generated CT
    generate_CT = visuals["G_fake"].data.clone().cpu().numpy()

    # Transpose and unnormalize
    if "std" in opt_variant.dataset_class or "baseline" in opt_variant.dataset_class:
        generate_CT_transpose = generate_CT
    else:
        generate_CT_transpose = np.transpose(generate_CT, (0, 2, 1, 3))

    generate_CT_transpose = tensor_back_to_unnormalization(
        generate_CT_transpose, opt_variant.CT_MEAN_STD[0], opt_variant.CT_MEAN_STD[1]
    )
    generate_CT_transpose = np.clip(generate_CT_transpose, 0, 1)

    sample = {
        "name": patient_data["patient_id"],
        "fake": generate_CT_transpose[0],
        "frontal": frontal_arr,
        "lateral": lateral_arr,
        "note": patient_data.get("note"),
        "model_variant": model_variant,
    }

    del gan_model, visuals
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return sample


def create_pdf_visualization(samples, output_path, checkpoint_num):
    """
    Create a PDF with each sample on a page showing:
    - Top row: frontal and lateral xrays
    - Below: Generated CT from 4 model variants side-by-side (Original | Synthetic | Real | Mixed)
    """
    # Group samples by patient name - each group has 4 variants
    grouped = OrderedDict()
    for sample in samples:
        name = sample["name"]
        if name not in grouped:
            grouped[name] = []
        grouped[name].append(sample)

    with PdfPages(str(output_path)) as pdf:
        for name, variant_samples in tqdm(grouped.items(), desc="Creating PDF pages"):
            # Build dict keyed by variant for easy access
            by_variant = {s["model_variant"]: s for s in variant_samples}

            # Get common data (same across variants)
            frontal = variant_samples[0]["frontal"]
            lateral = variant_samples[0].get("lateral")
            note = variant_samples[0].get("note")

            # Get fake CTs for computing shared vmin/vmax
            fake_cts = {k: v["fake"] for k, v in by_variant.items()}

            # Determine number of slices to show (every 10th slice)
            step = 10
            depth = list(fake_cts.values())[0].shape[0]
            slice_indices = list(range(0, depth, step))
            if len(slice_indices) == 0:
                slice_indices = [depth // 2]
            if len(slice_indices) > 15:
                slice_indices = slice_indices[:15]

            n_slices = len(slice_indices)

            # Layout: 4 columns for variants + 1 row for xrays at top
            # Columns: [Original | Synthetic | Real | Mixed]
            fig_height = 2 + n_slices * 2.5
            fig = plt.figure(figsize=(20, fig_height))

            # Title
            title_str = f"Sample: {name}"
            if note:
                title_str += f" ({note})"
            fig.suptitle(title_str, fontsize=14, fontweight="bold", y=0.98)

            # X-ray row at top
            gs_xray = fig.add_gridspec(
                nrows=1,
                ncols=2,
                wspace=0.05,
                top=0.94,
                bottom=0.88,
                left=0.02,
                right=0.98,
            )

            if frontal is not None:
                ax_x1 = fig.add_subplot(gs_xray[0])
                xray1_display = frontal.squeeze() if frontal.ndim > 2 else frontal
                ax_x1.imshow(xray1_display, cmap="gray", interpolation="nearest")
                ax_x1.set_title("Frontal X-Ray", fontsize=10)
                ax_x1.axis("off")
            else:
                ax_x1 = fig.add_subplot(gs_xray[0])
                ax_x1.text(0.5, 0.5, "No Frontal X-Ray", ha="center", va="center")
                ax_x1.axis("off")

            if lateral is not None:
                ax_x2 = fig.add_subplot(gs_xray[1])
                xray2_display = lateral.squeeze() if lateral.ndim > 2 else lateral
                ax_x2.imshow(xray2_display, cmap="gray", interpolation="nearest")
                ax_x2.set_title("Lateral X-Ray", fontsize=10)
                ax_x2.axis("off")
            else:
                ax_x2 = fig.add_subplot(gs_xray[1])
                ax_x2.text(0.5, 0.5, "No Lateral X-Ray", ha="center", va="center")
                ax_x2.axis("off")

            # CT slices: each row has 3 columns [Model C | Model E | Model M]
            gs_ct = fig.add_gridspec(
                nrows=n_slices,
                ncols=3,
                height_ratios=[1.0] * n_slices,
                width_ratios=[1, 1, 1],
                hspace=0.15,
                wspace=0.05,
                top=0.85,
                bottom=0.02,
                left=0.02,
                right=0.98,
            )

            for row_idx, slice_idx in enumerate(slice_indices):
                # Get all variant slices and compute shared vmin/vmax
                all_min = float("inf")
                all_max = float("-inf")
                variant_slices = {}
                for variant_key, _ in MODEL_VARIANTS:
                    if variant_key in fake_cts:
                        fake_slice = fake_cts[variant_key][slice_idx]
                        variant_slices[variant_key] = fake_slice
                        all_min = min(all_min, np.nanmin(fake_slice))
                        all_max = max(all_max, np.nanmax(fake_slice))

                # Variant slices (columns 0-3)
                for col_idx, (variant_key, label) in enumerate(MODEL_VARIANTS):
                    ax_var = fig.add_subplot(gs_ct[row_idx, col_idx])
                    if variant_key in variant_slices:
                        ax_var.imshow(
                            variant_slices[variant_key],
                            cmap="gray",
                            vmin=all_min,
                            vmax=all_max,
                            interpolation="nearest",
                        )
                        if row_idx == 0:
                            ax_var.set_title(f"{label}", fontsize=9)
                    else:
                        ax_var.text(0.5, 0.5, "N/A", ha="center", va="center")
                    ax_var.axis("off")

            pdf.savefig(fig, dpi=150)
            plt.close(fig)


def create_html_visualization(samples, output_dir, checkpoint_num):
    """
    Create per-patient HTML visualizations with:
    - Patient name
    - Frontal and lateral xray images
    - Generated CT from 4 model variants side-by-side
    """
    # Group samples by patient name - each group has 4 variants
    grouped = OrderedDict()
    for sample in samples:
        name = sample["name"]
        if name not in grouped:
            grouped[name] = []
        grouped[name].append(sample)

    # Create main output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, variant_samples in tqdm(
        grouped.items(), desc="Creating HTML per patient"
    ):
        # Build dict keyed by variant for easy access
        by_variant = {s["model_variant"]: s for s in variant_samples}

        # Get common data
        frontal = variant_samples[0]["frontal"]
        lateral = variant_samples[0].get("lateral")
        note = variant_samples[0].get("note")
        fake_cts = {k: v["fake"] for k, v in by_variant.items()}

        patient_dir = output_dir / name
        patient_dir.mkdir(parents=True, exist_ok=True)

        # Determine number of slices to show (every 10th slice)
        step = 10
        depth = list(fake_cts.values())[0].shape[0]
        slice_indices = list(range(0, depth, step))
        if len(slice_indices) == 0:
            slice_indices = [depth // 2]
        if len(slice_indices) > 15:
            slice_indices = slice_indices[:15]

        # Save xray images if available
        frontal_path = None
        lateral_path = None

        if frontal is not None:
            fig_x1, ax_x1 = plt.subplots(figsize=(6, 6))
            xray1_display = frontal.squeeze() if frontal.ndim > 2 else frontal
            ax_x1.imshow(xray1_display, cmap="gray", interpolation="nearest")
            ax_x1.set_title("Frontal X-Ray")
            ax_x1.axis("off")
            frontal_path = patient_dir / "frontal.png"
            fig_x1.savefig(str(frontal_path), dpi=100, bbox_inches="tight")
            plt.close(fig_x1)

        if lateral is not None:
            fig_x2, ax_x2 = plt.subplots(figsize=(6, 6))
            xray2_display = lateral.squeeze() if lateral.ndim > 2 else lateral
            ax_x2.imshow(xray2_display, cmap="gray", interpolation="nearest")
            ax_x2.set_title("Lateral X-Ray")
            ax_x2.axis("off")
            lateral_path = patient_dir / "lateral.png"
            fig_x2.savefig(str(lateral_path), dpi=100, bbox_inches="tight")
            plt.close(fig_x2)

        # Save variant CT slices
        variant_slice_paths = {variant_key: [] for variant_key, _ in MODEL_VARIANTS}
        for slice_idx in slice_indices:
            # Get all variant slices and compute shared vmin/vmax
            all_min = float("inf")
            all_max = float("-inf")
            variant_slices = {}
            for variant_key, _ in MODEL_VARIANTS:
                if variant_key in fake_cts:
                    fake_slice = fake_cts[variant_key][slice_idx]
                    variant_slices[variant_key] = fake_slice
                    all_min = min(all_min, np.nanmin(fake_slice))
                    all_max = max(all_max, np.nanmax(fake_slice))

            # Save 4 variant slices side-by-side
            fig, axes = plt.subplots(1, 4, figsize=(20, 5))
            for col_idx, (variant_key, label) in enumerate(MODEL_VARIANTS):
                if variant_key in variant_slices:
                    axes[col_idx].imshow(
                        variant_slices[variant_key],
                        cmap="gray",
                        vmin=all_min,
                        vmax=all_max,
                        interpolation="nearest",
                    )
                    axes[col_idx].set_title(f"{label}", fontsize=10)
                else:
                    axes[col_idx].text(0.5, 0.5, "N/A", ha="center", va="center")
                axes[col_idx].axis("off")

            slice_path = patient_dir / f"slice_{slice_idx}.png"
            fig.savefig(str(slice_path), dpi=100, bbox_inches="tight")
            plt.close(fig)

            for variant_key, _ in MODEL_VARIANTS:
                variant_slice_paths[variant_key].append(slice_path)

        # Generate HTML
        title_str = f"Patient: {name}"
        if note:
            title_str += f" ({note})"

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title_str}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        h1 {{ color: #333; text-align: center; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .patient-info {{ background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}
        .xray-container {{ display: flex; justify-content: center; gap: 20px; margin: 20px 0; }}
        .xray-container img {{ max-width: 300px; border: 2px solid #ddd; border-radius: 4px; }}
        .ct-table {{ display: flex; flex-direction: column; align-items: center; gap: 10px; margin: 20px 0; }}
        .ct-row {{ display: flex; justify-content: center; gap: 20px; }}
        .ct-col {{ text-align: center; }}
        .ct-col img {{ display: block; margin: 0 auto; border: 1px solid #999; max-width: 250px; }}
        .slice-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .col-header {{ font-weight: bold; margin-bottom: 10px; padding: 5px 10px; border-radius: 4px; }}
        .header-original {{ background-color: #e8f5e9; }}
        .header-synthetic {{ background-color: #fff3e0; }}
        .header-mixed {{ background-color: #e0f7fa; }}
        .metadata {{ color: #777; font-size: 14px; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>{title_str}</h1>
    <div class="patient-info">
        <strong>Patient ID:</strong> {name} | <strong>CT Depth:</strong> {depth} slices
    </div>

    <h2>Input X-Rays</h2>
    <div class="xray-container">
"""
        if frontal_path:
            html_content += f'        <div><img src="{frontal_path.name}" alt="Frontal X-Ray"><br><center>Frontal</center></div>\n'
        if lateral_path:
            html_content += f'        <div><img src="{lateral_path.name}" alt="Lateral X-Ray"><br><center>Lateral</center></div>\n'
        if frontal_path is None and lateral_path is None:
            html_content += (
                "        <p>No x-ray images available for this sample.</p>\n"
            )

        html_content += """    </div>

    <h2>CT Comparison: Generated from 4 Model Variants</h2>
    <div class="ct-table">
"""
        for slice_idx in slice_indices:
            slice_path = variant_slice_paths[MODEL_VARIANTS[0][0]][
                slice_indices.index(slice_idx)
            ]
            html_content += f"""        <div class="ct-row">
"""
            for variant_key, label in MODEL_VARIANTS:
                html_content += f"""            <div class="ct-col">
                <div class="col-header header-{variant_key[:10]}">{label}</div>
                <img src="{slice_path.name}" alt="{label} Slice {slice_idx}">
                <div class="slice-label">Slice {slice_idx}</div>
            </div>
"""
            html_content += "        </div>\n"

        html_content += """    </div>
    <div class="metadata">
        <p>Generated by indiana_comparison_visuals.py | AECT-GAN 3DGAN</p>
    </div>
</body>
</html>
"""

        html_path = patient_dir / f"{name}.html"
        with open(str(html_path), "w") as f:
            f.write(html_content)


# ------------------------------------------------------------------------------
# Checkpoint helpers for resumable processing
# ------------------------------------------------------------------------------


def get_checkpoint_path(result_dir, checkpoint_num):
    """Get the checkpoint file path."""
    return result_dir / f"checkpoint_{checkpoint_num}.pkl"


def save_checkpoint(result_dir, checkpoint_num, samples, processed_keys):
    """Save current progress to checkpoint file."""
    checkpoint_path = get_checkpoint_path(result_dir, checkpoint_num)
    # Convert sets to lists for pickling
    checkpoint_data = {
        "samples": samples,
        "processed_keys": [list(k) for k in processed_keys],
    }
    with open(checkpoint_path, "wb") as f:
        pickle.dump(checkpoint_data, f)
    print(f"Checkpoint saved: {checkpoint_path} ({len(samples)} samples)")


def load_checkpoint(result_dir, checkpoint_num):
    """Load progress from checkpoint file if it exists."""
    checkpoint_path = get_checkpoint_path(result_dir, checkpoint_num)
    if checkpoint_path.exists():
        with open(checkpoint_path, "rb") as f:
            checkpoint_data = pickle.load(f)
        # Convert lists back to sets
        processed_keys = {tuple(k) for k in checkpoint_data["processed_keys"]}
        print(
            f"Loaded checkpoint: {checkpoint_path} ({len(checkpoint_data['samples'])} samples already processed)"
        )
        return checkpoint_data["samples"], processed_keys
    return [], set()


def generate_visualizations(args):
    # Check gpu
    if args.gpuid == "":
        args.gpu_ids = []
    else:
        if torch.cuda.is_available():
            split_gpu = str(args.gpuid).split(",")
            args.gpu_ids = [int(i) for i in split_gpu]
        else:
            print("There is no gpu!")
            exit(0)

    # Check point
    if args.check_point is None:
        args.epoch_count = 1
    else:
        args.epoch_count = int(args.check_point)

    checkpoint_num = args.epoch_count

    # Merge config with yaml
    if args.ymlpath is not None:
        cfg_from_yaml(args.ymlpath)
    else:
        # Use default config for multiview2500
        default_yml = os.path.join(
            script_dir, "experiment", "multiview2500", "d2_multiview2500.yml"
        )
        if os.path.exists(default_yml):
            cfg_from_yaml(default_yml)

    # Merge config with argparse
    opt = copy.deepcopy(cfg)
    opt = merge_dict_and_yaml(args.__dict__, opt)
    print_easy_dict(opt)

    opt.serial_batches = True

    # Get fine_size from DATA_AUG config (default to 128)
    fine_size = (
        opt.DATA_AUG.fine_size
        if hasattr(opt, "DATA_AUG") and hasattr(opt.DATA_AUG, "fine_size")
        else 128
    )

    # Group images by patient
    print(f"Reading images from {args.indiana_dir}...")
    patient_groups = group_images_by_patient(args.indiana_dir)
    total_patients = len(patient_groups)
    print(f"Found {total_patients} patients")

    # Filter to patients with at least 2 images BEFORE classification
    patients_with_2plus = {
        pid: paths for pid, paths in patient_groups.items() if len(paths) >= 2
    }
    print(f"Found {len(patients_with_2plus)} patients with 2+ images (potential pairs)")

    # Limit to first N patients with 2+ images BEFORE classification
    if args.how_many > 0 and len(patients_with_2plus) > args.how_many:
        patients_with_2plus = dict(list(patients_with_2plus.items())[: args.how_many])
        print(f"Limited to first {args.how_many} patients for classification")

    # Classify and pair images
    print("Classifying and pairing images...")
    paired_samples = classify_and_pair_images(
        patients_with_2plus, args.classifier_weights, args.cache, fine_size=fine_size
    )
    print(f"Found {len(paired_samples)} patients with valid pairs")

    if len(paired_samples) == 0:
        print("No valid patient pairs found. Exiting.")
        return []

    # Output directory structure: outputs/supplementary/data/{data_path}/{model_name}/indiana/checkpoint_{num}
    # Following indiana_supplementary_visuals.py pattern
    # Since we run all 4 variants together, use "all_variants" as model_name placeholder
    data_path = Path(args.data)
    if data_path.parts[0] == "data":
        data_path = Path(*data_path.parts[1:])  # Strip leading 'data'
    result_dir = (
        Path("outputs")
        / "supplementary"
        / "data"
        / data_path
        / "comparison_indiana"
        / f"checkpoint_{checkpoint_num}"
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    # Load checkpoint if exists for resuming after interruption
    samples, processed_keys = load_checkpoint(result_dir, checkpoint_num)

    # For each patient, run inference with all model variants
    for patient_data in tqdm(paired_samples, desc="Processing patients"):
        patient_id = patient_data["patient_id"]

        # Process all 4 variants for this patient
        for model_variant, _ in MODEL_VARIANTS:
            key = (patient_id, model_variant)

            # Skip if already processed (resume support)
            if key in processed_keys:
                continue

            try:
                sample = run_inference_single(
                    model_variant=model_variant,
                    model_root=args.model_root,
                    patient_data=patient_data,
                    opt=opt,
                )
                samples.append(sample)
                processed_keys.add(key)
            except Exception as e:
                print(
                    f"Error processing {patient_id} with variant {model_variant}: {e}"
                )
                import traceback

                traceback.print_exc()
                continue

        # Save checkpoint after each patient (all variants processed)
        save_checkpoint(result_dir, checkpoint_num, samples, processed_keys)

    if len(samples) == 0:
        print("No samples generated. Exiting.")
        return []

    # Set output_dir to result_dir to follow the supplementary structure
    output_dir = result_dir

    # Create PDF
    print("Creating PDF visualization...")
    pdf_path = output_dir / f"indiana_comparison_visuals_{checkpoint_num}.pdf"
    create_pdf_visualization(samples, pdf_path, checkpoint_num)
    print(f"PDF saved to: {pdf_path}")



    # Create HTML per patient
    print("Creating HTML visualizations per patient...")
    html_dir = result_dir / "html_per_patient"
    create_html_visualization(samples, html_dir, checkpoint_num)
    print(f"HTML visualizations saved to: {html_dir}")

    print("Done! All visualizations generated.")
    return samples


if __name__ == "__main__":
    args = parse_args()
    generate_visualizations(args)
