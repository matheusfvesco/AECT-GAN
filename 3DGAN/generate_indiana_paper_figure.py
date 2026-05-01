#!/usr/bin/env python3
"""
generate_indiana_paper_figure.py

Generates a publication-ready PNG figure comparing CT generation for the
Indiana University case CXR1070 across 4 model variants.

Layout: 5 columns x 8 rows
    Column 1: Input X-Rays (Frontal + Lateral stacked vertically)
    Columns 2-5: Cheng et al. | Synthetic | Real | Mixed

8 rows show middle 80 slices (every 10th from indices 24-103).

Usage:
    python generate_indiana_paper_figure.py
"""

import argparse
import copy
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(script_dir, "lib")
sys.path.insert(0, lib_path)

from lib.config.config import cfg_from_yaml, cfg, merge_dict_and_yaml, print_easy_dict
from lib.model.factory import get_model
from lib.utils.visualizer import tensor_back_to_unnormalization
from lib.xray_classifier import classify_xray_view, _preprocess_array


MODEL_VARIANTS = [
    ("d2_multiview2500", "Model C"),
    ("multiview-GAN-dataset-complete-clipped-shifted", "Model E"),
    ("multiview-GAN-dataset-complete-clipped-shifted-real_mixed", "Model M"),
]

# Layout configuration
BASE_COLS = 1  # Input X-rays only
ORIGINAL_NCOLS = 5
ORIGINAL_FIG_WIDTH = 14.0


def calc_fig_width(ncols):
    return ORIGINAL_FIG_WIDTH * ncols / ORIGINAL_NCOLS


CT_DEPTH = 128
MIDDLE_SLICES = 80
SLICES_PER_ROW = 8
SKIP_TOP_BOTTOM = (CT_DEPTH - MIDDLE_SLICES) // 2


def load_classification_cache(cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    return {}


def save_classification_to_cache(cache_path, image_path, view_type):
    cache = load_classification_cache(cache_path)
    cache[str(image_path)] = view_type
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2)


def get_cached_or_classify(image_path, cache_path, classifier_weights, img_array):
    cache = load_classification_cache(cache_path)
    image_path_str = str(image_path)
    if image_path_str in cache:
        return cache[image_path_str]
    view_type = classify_xray_view(img_array, weights_path=classifier_weights)
    save_classification_to_cache(cache_path, image_path_str, view_type)
    return view_type


def parse_args():
    parse = argparse.ArgumentParser(description="Generate Indiana Paper Figure")
    parse.add_argument(
        "--indiana_dir",
        type=str,
        default="data/indiana_png",
        help="path to Indiana PNG dataset directory",
    )
    parse.add_argument(
        "--patient_id", type=str, default="CXR1070", help="patient ID to visualize"
    )
    parse.add_argument(
        "--ymlpath",
        type=str,
        default="experiment/multiview2500/d2_multiview2500.yml",
        help="config yaml path",
    )
    parse.add_argument("--gpu", type=str, default="0", dest="gpuid", help="gpu id")
    parse.add_argument(
        "--data",
        type=str,
        default="data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN",
        help="data identifier",
    )
    parse.add_argument(
        "--dataset_class",
        type=str,
        default="align_ct_xray_views_std",
        help="Dataset class",
    )
    parse.add_argument(
        "--model_class", type=str, default="MultiView-AECT-GAN", help="Model class"
    )
    parse.add_argument(
        "--check_point", type=str, default="90", help="which epoch to load"
    )
    parse.add_argument(
        "--num_slices",
        type=int,
        default=8,
        help="number of CT slices to display (rows)",
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
        "--tag", type=str, default="multiview2500", help="tag for model save"
    )
    parse.add_argument(
        "--model_root",
        type=str,
        default="save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN",
        help="Root path to model weights directory",
    )
    parse.add_argument(
        "--classifier_weights",
        type=str,
        default="save_models/xray_classifier.pth",
        help="path to xray classifier weights",
    )
    parse.add_argument(
        "--cache",
        type=str,
        default="data/indiana_xray_classification_cache.json",
        help="path to classification cache JSON file",
    )
    parse.add_argument(
        "--output",
        type=str,
        default=None,
        help="output PNG filename (default: indiana_{patient_id}_figure.png)",
    )
    args = parse.parse_args()
    return args


def group_images_by_patient(indiana_dir):
    indiana_dir = Path(indiana_dir)
    files = sorted([f for f in os.listdir(indiana_dir) if f.endswith(".png")])

    groups = {}
    for f in files:
        name_without_ext = f.replace(".png", "")
        parts = name_without_ext.split("_")

        if parts[0] == "CXR":
            if len(parts) >= 3 and parts[2] == "IM":
                patient_id = "_".join(parts[:2])
            elif len(parts) >= 2 and parts[1].startswith("IM"):
                patient_id = parts[0]
            elif len(parts) >= 2 and not parts[1].startswith("IM"):
                patient_id = "_".join(parts[:2])
            else:
                patient_id = parts[0]
        else:
            patient_id = parts[0]

        if patient_id not in groups:
            groups[patient_id] = []
        groups[patient_id].append(indiana_dir / f)

    return groups


def classify_and_pair_images(
    patient_groups, classifier_weights, cache_path, fine_size=128
):
    paired_samples = []

    for patient_id, image_paths in patient_groups.items():
        if len(image_paths) < 2:
            continue

        patient_images = []
        for img_path in image_paths:
            try:
                img = Image.open(img_path).convert("L")
                img = img.resize((fine_size, fine_size), Image.LANCZOS)
                img_arr = np.array(img).astype(np.float32) / 255.0
                patient_images.append({"path": img_path, "array": img_arr})
            except Exception as e:
                print(f"Error loading {img_path}: {e}")
                continue

        if len(patient_images) < 2:
            continue

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

        if frontal_images and lateral_images:
            paired_samples.append(
                {
                    "patient_id": patient_id,
                    "frontal": frontal_images[0],
                    "lateral": lateral_images[0],
                }
            )
        elif len(frontal_images) >= 2:
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


def run_inference_single(model_variant, model_root, patient_data, opt):
    load_path = f"{model_root.rstrip('/')}/{model_variant}/checkpoint"

    opt_variant = copy.deepcopy(opt)
    opt_variant.load_path = load_path

    gan_model = get_model(opt_variant.model_class)()
    gan_model.eval()
    gan_model.init_process(opt_variant)
    gan_model.setup(opt_variant)

    if "batch" in opt_variant.norm_G:
        gan_model.eval()
    elif "instance" in opt_variant.norm_G:
        gan_model.eval()
        for name, m in gan_model.named_modules():
            if m.__class__.__name__.startswith("InstanceNorm"):
                m.train()
    else:
        raise NotImplementedError()

    frontal_arr = patient_data["frontal"]["array"]
    lateral_arr = patient_data["lateral"]["array"]

    ct_tensor = torch.zeros(1, 128, 128, 128)
    frontal_tensor = torch.from_numpy(frontal_arr).unsqueeze(0).unsqueeze(0)
    lateral_tensor = torch.from_numpy(lateral_arr).unsqueeze(0).unsqueeze(0)

    if hasattr(opt_variant, "XRAY1_MIN_MAX") and opt_variant.XRAY1_MIN_MAX is not None:
        xmin, xmax = opt_variant.XRAY1_MIN_MAX
        if xmax != xmin:
            frontal_tensor = (frontal_tensor - xmin) / (xmax - xmin)

    if hasattr(opt_variant, "XRAY2_MIN_MAX") and opt_variant.XRAY2_MIN_MAX is not None:
        xmin, xmax = opt_variant.XRAY2_MIN_MAX
        if xmax != xmin:
            lateral_tensor = (lateral_tensor - xmin) / (xmax - xmin)

    frontal_tensor = torch.clamp(frontal_tensor, 0, 1)
    lateral_tensor = torch.clamp(lateral_tensor, 0, 1)

    frontal_path = str(patient_data["frontal"]["path"])
    lateral_path = str(patient_data["lateral"]["path"])

    gan_model.set_input(
        (ct_tensor, (frontal_tensor, lateral_tensor), frontal_path, lateral_path)
    )
    gan_model.test()

    visuals = gan_model.get_current_visuals()
    generate_CT = visuals["G_fake"].data.clone().cpu().numpy()

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


def main():
    args = parse_args()

    if args.gpuid == "":
        args.gpu_ids = []
    else:
        if torch.cuda.is_available():
            args.gpu_ids = [int(args.gpuid)]
        else:
            print("There is no gpu!")
            exit(0)

    args.epoch_count = int(args.check_point)
    checkpoint_num = args.epoch_count

    cfg_from_yaml(args.ymlpath)

    opt = copy.deepcopy(cfg)
    opt = merge_dict_and_yaml(vars(args), opt)
    print_easy_dict(opt)

    opt.serial_batches = True

    fine_size = (
        opt.DATA_AUG.fine_size
        if hasattr(opt, "DATA_AUG") and hasattr(opt.DATA_AUG, "fine_size")
        else 128
    )

    print(f"Loading X-rays for patient {args.patient_id}...")

    patient_images = []
    for f in sorted(os.listdir(args.indiana_dir)):
        if not f.endswith(".png") or not f.startswith(args.patient_id):
            continue
        img_path = Path(args.indiana_dir) / f
        try:
            img = Image.open(img_path).convert("L")
            img = img.resize((fine_size, fine_size), Image.LANCZOS)
            img_arr = np.array(img).astype(np.float32) / 255.0
            patient_images.append({"path": img_path, "array": img_arr, "name": f})
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            continue

    if len(patient_images) < 2:
        print(f"Patient {args.patient_id} has fewer than 2 images, cannot pair")
        return

    frontal_images = []
    lateral_images = []
    for img_data in patient_images:
        view_type = get_cached_or_classify(
            img_data["path"], args.cache, args.classifier_weights, img_data["array"]
        )
        img_data["view"] = view_type
        if view_type == "frontal":
            frontal_images.append(img_data)
        else:
            lateral_images.append(img_data)

    if frontal_images and lateral_images:
        patient_data = {
            "patient_id": args.patient_id,
            "frontal": frontal_images[0],
            "lateral": lateral_images[0],
        }
    elif len(frontal_images) >= 2:
        patient_data = {
            "patient_id": args.patient_id,
            "frontal": frontal_images[0],
            "lateral": frontal_images[1],
            "note": "both_frontal",
        }
    elif len(lateral_images) >= 2:
        patient_data = {
            "patient_id": args.patient_id,
            "frontal": lateral_images[0],
            "lateral": lateral_images[1],
            "note": "both_lateral",
        }
    else:
        print(f"Could not find frontal/lateral pair for {args.patient_id}")
        return

    print(f"Processing patient {args.patient_id}...")

    results = {}
    for model_variant, label in MODEL_VARIANTS:
        print(f"  Running inference with {model_variant} ({label})...")
        sample = run_inference_single(
            model_variant=model_variant,
            model_root=args.model_root,
            patient_data=patient_data,
            opt=opt,
        )
        results[model_variant] = sample

    middle_start = SKIP_TOP_BOTTOM
    middle_end = CT_DEPTH - SKIP_TOP_BOTTOM
    slice_step = max(1, MIDDLE_SLICES // args.num_slices)
    slice_indices = list(range(middle_start, middle_end, slice_step))
    slice_indices = slice_indices[: args.num_slices]

    ncols = BASE_COLS + len(MODEL_VARIANTS)
    fig_width = calc_fig_width(ncols)
    fig_height = 4.0 + args.num_slices * 2.5
    fig = plt.figure(figsize=(fig_width, fig_height))

    gs = gridspec.GridSpec(
        nrows=args.num_slices + 1,
        ncols=ncols,
        height_ratios=[0.6] + [1.0] * args.num_slices,
        width_ratios=[1] * ncols,
        hspace=0.05,
        wspace=0.05,
        top=0.98,
        bottom=0.02,
        left=0.03,
        right=0.97,
    )

    col_labels = ["Input\nX-Rays"] + [label for _, label in MODEL_VARIANTS]
    for col_idx, label in enumerate(col_labels):
        ax_header = fig.add_subplot(gs[0, col_idx])
        ax_header.text(0.5, 0.5, label, ha="center", va="center", fontsize=40)
        ax_header.axis("off")

    xray_combined = np.vstack(
        [patient_data["frontal"]["array"], patient_data["lateral"]["array"]]
    )
    ax_xrays = fig.add_subplot(gs[1:, 0])
    ax_xrays.imshow(xray_combined, cmap="gray", interpolation="nearest")
    ax_xrays.axis("off")

    all_min = float("inf")
    all_max = float("-inf")
    for model_variant, _ in MODEL_VARIANTS:
        fake = results[model_variant]["fake"]
        for idx in slice_indices:
            slice_data = fake[idx]
            all_min = min(all_min, np.nanmin(slice_data))
            all_max = max(all_max, np.nanmax(slice_data))

    for row_idx, slice_idx in enumerate(slice_indices):
        for col_idx, (model_variant, label) in enumerate(MODEL_VARIANTS):
            ax = fig.add_subplot(gs[row_idx + 1, col_idx + 1])
            fake = results[model_variant]["fake"]
            ax.imshow(
                fake[slice_idx],
                cmap="gray",
                vmin=all_min,
                vmax=all_max,
                interpolation="nearest",
            )
            ax.axis("off")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "comparison_plots")
    os.makedirs(output_dir, exist_ok=True)

    output_file = (
        args.output if args.output else f"indiana_{args.patient_id}_figure.png"
    )
    output_path = os.path.join(output_dir, output_file)

    plt.savefig(
        output_path.replace(".png", ".pdf"),
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.03,
    )
    plt.savefig(
        output_path.replace(".png", ".svg"), bbox_inches="tight", pad_inches=0.03
    )
    plt.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)

    print(
        f"Figures saved to: {output_path.replace('.png', '.pdf')}, {output_path.replace('.png', '.svg')}, {output_path}"
    )


if __name__ == "__main__":
    main()
