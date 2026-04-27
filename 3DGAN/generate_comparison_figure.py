#!/usr/bin/env python3
"""
generate_realtest_paper_figure.py

Generates a publication-ready PNG figure comparing CT generation for a
real-test sample across 4 model variants, with ground truth CT shown.

Layout: 6 columns x N rows
    Column 1: Input X-Rays (Frontal + Lateral stacked vertically)
    Column 2: Ground Truth CT
    Columns 3-6: Cheng et al. | Synthetic | Real | Mixed

Usage:
    python generate_realtest_paper_figure.py --tag real_test --patient_id LIDC-IDRI-0003 --num_slices 8
"""

import argparse
import copy
import os
import sys
from pathlib import Path

import numpy as np
import torch
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(script_dir, "lib")
sys.path.insert(0, lib_path)

from lib.config.config import cfg_from_yaml, cfg, merge_dict_and_yaml, print_easy_dict
from lib.model.factory import get_model
from lib.utils.visualizer import tensor_back_to_unnormalization
from lib.dataset.factory import get_dataset


MODEL_VARIANTS = [
    ("d2_multiview2500", "Cheng et al."),
    ("multiview-GAN-dataset-complete-clipped-shifted", "Synthetic"),
    ("multiview-GAN-dataset-complete-clipped-shifted-real", "Real"),
    ("multiview-GAN-dataset-complete-clipped-shifted-real_mixed", "Mixed"),
]

MODEL_VARIANTS_ORIGINAL = [
    ("multiview-GAN-dataset-complete-clipped-shifted", "Synthetic"),
    ("multiview-GAN-dataset-complete-clipped-shifted-real", "Real"),
    ("multiview-GAN-dataset-complete-clipped-shifted-real_mixed", "Mixed"),
]


def extract_patient_base_id(patient_str):
    """Extract base patient ID from format like LIDC-IDRI-0256.20000101.8658.4.1 -> LIDC-IDRI-0256"""
    return patient_str.split(".")[0]


def find_patient_in_test_file(patient_id, test_file_path):
    """Find patient in test.txt and return the full line (with date suffix)"""
    if not os.path.exists(test_file_path):
        return None
    base_id = extract_patient_base_id(patient_id)
    with open(test_file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                if extract_patient_base_id(line) == base_id:
                    return line
    return None


def load_original_sample(patient_id, opt):
    """Load sample from original LIDC-HDF5-256 dataset for --original mode"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    original_dataroot = os.path.join(script_dir, "data/LIDC-HDF5-256")
    original_datasetfile = os.path.join(script_dir, "data/test.txt")

    matched_line = find_patient_in_test_file(patient_id, original_datasetfile)
    if matched_line is None:
        raise ValueError(f"Patient {patient_id} not found in original test.txt")

    opt_original = copy.deepcopy(opt)
    opt_original.dataroot = original_dataroot
    opt_original.datasetfile = original_datasetfile

    datasetClass, _, dataTestClass, collateClass = get_dataset(
        opt_original.dataset_class
    )
    dataset = datasetClass(opt_original)
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=1,
        shuffle=False,
        num_workers=int(opt_original.nThreads),
        collate_fn=collateClass,
    )

    sample = None
    for epoch_i, data in enumerate(dataloader):
        ct, xrays, file_paths = data
        path_str = file_paths[0]
        sample_name = Path(path_str).parent.name

        if sample_name == matched_line:
            sample = data
            print(f"Found original patient {matched_line} at index {epoch_i}")
            break

    if sample is None:
        raise ValueError(f"Patient {matched_line} not found in original dataset")

    return sample, matched_line
    base_id = extract_patient_base_id(patient_id)
    with open(test_file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                if extract_patient_base_id(line) == base_id:
                    return line
    return None


CT_DEPTH = 128
MIDDLE_SLICES = 80
SKIP_TOP_BOTTOM = (CT_DEPTH - MIDDLE_SLICES) // 2


def parse_args():
    parse = argparse.ArgumentParser(description="Generate Real-Test Paper Figure")
    parse.add_argument(
        "--patient_id", type=str, required=True, help="patient ID to visualize"
    )
    parse.add_argument(
        "--num_slices",
        type=int,
        default=8,
        help="number of CT slices to display (rows)",
    )
    parse.add_argument(
        "--tag", type=str, required=True, help="distinct tag for output directory"
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
        "--dataroot",
        type=str,
        default="data/GAN-dataset-complete-clipped-shifted-real",
        help="input data root",
    )
    parse.add_argument(
        "--datasetfile",
        type=str,
        default="data/real_test.txt",
        help="Test file path",
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
        default="save_models/multiView_CTGAN/data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN",
        help="Root path to model weights directory",
    )
    parse.add_argument(
        "--output",
        type=str,
        default=None,
        help="output PNG filename (default: {tag}_{patient_id}_figure.png)",
    )
    parse.add_argument(
        "--original",
        action="store_true",
        dest="original",
        help="if specified, create plot with real xrays and original GT comparison",
    )
    args = parse.parse_args()
    return args


def run_inference_single(model_variant, model_root, data, opt):
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

    gan_model.set_input(data)
    gan_model.test()

    visuals = gan_model.get_current_visuals()
    img_path = gan_model.get_image_paths()

    name1 = os.path.splitext(os.path.basename(img_path[0][0]))[0]
    name2 = os.path.split(os.path.dirname(img_path[0][0]))[-1]
    name = name2 + "_" + name1

    generate_CT = visuals["G_fake"].data.clone().cpu().numpy()
    real_CT = visuals["G_real"].data.clone().cpu().numpy()

    if "std" in opt_variant.dataset_class or "baseline" in opt_variant.dataset_class:
        generate_CT_transpose = generate_CT
        real_CT_transpose = real_CT
    else:
        generate_CT_transpose = np.transpose(generate_CT, (0, 2, 1, 3))
        real_CT_transpose = np.transpose(real_CT, (0, 2, 1, 3))

    generate_CT_transpose = tensor_back_to_unnormalization(
        generate_CT_transpose, opt_variant.CT_MEAN_STD[0], opt_variant.CT_MEAN_STD[1]
    )
    real_CT_transpose = tensor_back_to_unnormalization(
        real_CT_transpose, opt_variant.CT_MEAN_STD[0], opt_variant.CT_MEAN_STD[1]
    )
    generate_CT_transpose = np.clip(generate_CT_transpose, 0, 1)
    real_CT_transpose = np.clip(real_CT_transpose, 0, 1)

    xray1 = None
    xray2 = None
    if "G_input1" in visuals:
        xray1 = visuals["G_input1"].data.clone().cpu().numpy()[0].astype(np.float32)
    if "G_input2" in visuals:
        xray2 = visuals["G_input2"].data.clone().cpu().numpy()[0].astype(np.float32)

    sample = {
        "name": name,
        "gt": real_CT_transpose[0],
        "fake": generate_CT_transpose[0],
        "xray1": xray1,
        "xray2": xray2,
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

    datasetClass, _, dataTestClass, collateClass = get_dataset(opt.dataset_class)
    opt.data_augmentation = dataTestClass

    dataset = datasetClass(opt)
    print("DataSet is {}".format(dataset.name))
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=1,
        shuffle=False,
        num_workers=int(opt.nThreads),
        collate_fn=collateClass,
    )

    dataset_size = len(dataloader)
    print("#Test images = %d" % dataset_size)

    sample = None
    target_sample_idx = None
    for epoch_i, data in enumerate(dataloader):
        ct, xrays, file_paths = data
        path_str = file_paths[0]
        sample_name = Path(path_str).parent.name

        if sample_name == args.patient_id:
            sample = data
            target_sample_idx = epoch_i
            print(f"Found patient {args.patient_id} at index {epoch_i}")
            break

    if sample is None:
        print(f"Patient {args.patient_id} not found in dataset")
        return

    print(f"Processing patient {args.patient_id}...")

    if args.original:
        results = {}
        for model_variant, label in MODEL_VARIANTS_ORIGINAL:
            print(f"  Running inference with {model_variant} ({label})...")
            result = run_inference_single(
                model_variant=model_variant,
                model_root=args.model_root,
                data=sample,
                opt=opt,
            )
            results[model_variant] = result

        print(f"Loading original sample from LIDC-HDF5-256...")
        original_sample, matched_patient_id = load_original_sample(args.patient_id, opt)

        cheng_variant = "d2_multiview2500"
        print(
            f"  Running inference with {cheng_variant} (Cheng et al.) on original data..."
        )
        result_cheng = run_inference_single(
            model_variant=cheng_variant,
            model_root=args.model_root,
            data=original_sample,
            opt=opt,
        )
        results[cheng_variant] = result_cheng

        xray1 = results[MODEL_VARIANTS_ORIGINAL[0][0]]["xray1"]
        xray2 = results[MODEL_VARIANTS_ORIGINAL[0][0]]["xray2"]
        gt_ct = results[MODEL_VARIANTS_ORIGINAL[0][0]]["gt"]

        middle_start = SKIP_TOP_BOTTOM
        middle_end = CT_DEPTH - SKIP_TOP_BOTTOM
        slice_step = max(1, MIDDLE_SLICES // args.num_slices)
        slice_indices = list(range(middle_start, middle_end, slice_step))
        slice_indices = slice_indices[: args.num_slices]

        fig_width = 8.5
        fig_height = 2.0 + args.num_slices * 1.25
        fig = plt.figure(figsize=(fig_width, fig_height))

        gs = gridspec.GridSpec(
            nrows=args.num_slices + 1,
            ncols=6,
            height_ratios=[0.6] + [1.0] * args.num_slices,
            width_ratios=[1, 1, 1, 1, 1, 1],
            hspace=0.05,
            wspace=0.05,
            top=0.98,
            bottom=0.02,
            left=0.03,
            right=0.97,
        )

        col_labels = [
            "Input\nX-Rays",
            "Ground\nTruth",
            "Cheng et al.",
            "Synthetic",
            "Real",
            "Mixed",
        ]
        for col_idx, label in enumerate(col_labels):
            ax_header = fig.add_subplot(gs[0, col_idx])
            ax_header.text(
                0.5, 0.5, label, ha="center", va="center", fontsize=9, fontweight="bold"
            )
            ax_header.axis("off")

        xray1_np = xray1.squeeze().astype(np.float32) if xray1.ndim > 2 else xray1
        xray2_np = xray2.squeeze().astype(np.float32) if xray2.ndim > 2 else xray2
        xray_combined = np.vstack([xray1_np, xray2_np])
        ax_xrays = fig.add_subplot(gs[1:, 0])
        ax_xrays.imshow(xray_combined, cmap="gray", interpolation="nearest")
        ax_xrays.axis("off")

        all_min = float("inf")
        all_max = float("-inf")
        for model_variant, _ in MODEL_VARIANTS_ORIGINAL:
            fake = results[model_variant]["fake"]
            for idx in slice_indices:
                slice_data = fake[idx]
                all_min = min(all_min, np.nanmin(slice_data))
                all_max = max(all_max, np.nanmax(slice_data))
        fake_cheng = results["d2_multiview2500"]["fake"]
        for idx in slice_indices:
            slice_data = fake_cheng[idx]
            all_min = min(all_min, np.nanmin(slice_data))
            all_max = max(all_max, np.nanmax(slice_data))

        for row_idx, slice_idx in enumerate(slice_indices):
            ax_gt = fig.add_subplot(gs[row_idx + 1, 1])
            ax_gt.imshow(
                gt_ct[slice_idx],
                cmap="gray",
                vmin=all_min,
                vmax=all_max,
                interpolation="nearest",
            )
            ax_gt.axis("off")

            ax_cheng = fig.add_subplot(gs[row_idx + 1, 2])
            ax_cheng.imshow(
                fake_cheng[slice_idx],
                cmap="gray",
                vmin=all_min,
                vmax=all_max,
                interpolation="nearest",
            )
            ax_cheng.axis("off")

            for col_idx, (model_variant, label) in enumerate(MODEL_VARIANTS_ORIGINAL):
                ax = fig.add_subplot(gs[row_idx + 1, col_idx + 3])
                fake = results[model_variant]["fake"]
                ax.imshow(
                    fake[slice_idx],
                    cmap="gray",
                    vmin=all_min,
                    vmax=all_max,
                    interpolation="nearest",
                )
                ax.axis("off")

        output_file = (
            args.output if args.output else f"{args.tag}_{args.patient_id}_figure.png"
        )

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "comparison_plots")
        os.makedirs(output_dir, exist_ok=True)

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
    else:
        results = {}
        for model_variant, label in MODEL_VARIANTS:
            print(f"  Running inference with {model_variant} ({label})...")
            result = run_inference_single(
                model_variant=model_variant,
                model_root=args.model_root,
                data=sample,
                opt=opt,
            )
            results[model_variant] = result

        xray1 = results[MODEL_VARIANTS[0][0]]["xray1"]
        xray2 = results[MODEL_VARIANTS[0][0]]["xray2"]
        gt_ct = results[MODEL_VARIANTS[0][0]]["gt"]

        middle_start = SKIP_TOP_BOTTOM
        middle_end = CT_DEPTH - SKIP_TOP_BOTTOM
        slice_step = max(1, MIDDLE_SLICES // args.num_slices)
        slice_indices = list(range(middle_start, middle_end, slice_step))
        slice_indices = slice_indices[: args.num_slices]

        fig_width = 8.5
        fig_height = 2.0 + args.num_slices * 1.25
        fig = plt.figure(figsize=(fig_width, fig_height))

        gs = gridspec.GridSpec(
            nrows=args.num_slices + 1,
            ncols=6,
            height_ratios=[0.6] + [1.0] * args.num_slices,
            width_ratios=[1, 1, 1, 1, 1, 1],
            hspace=0.05,
            wspace=0.05,
            top=0.98,
            bottom=0.02,
            left=0.03,
            right=0.97,
        )

        col_labels = [
            "Input\nX-Rays",
            "Ground\nTruth",
            "Cheng et al.",
            "Synthetic",
            "Real",
            "Mixed",
        ]
        for col_idx, label in enumerate(col_labels):
            ax_header = fig.add_subplot(gs[0, col_idx])
            ax_header.text(
                0.5, 0.5, label, ha="center", va="center", fontsize=9, fontweight="bold"
            )
            ax_header.axis("off")

        xray1_np = xray1.squeeze().astype(np.float32) if xray1.ndim > 2 else xray1
        xray2_np = xray2.squeeze().astype(np.float32) if xray2.ndim > 2 else xray2
        xray_combined = np.vstack([xray1_np, xray2_np])
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
            ax_gt = fig.add_subplot(gs[row_idx + 1, 1])
            ax_gt.imshow(
                gt_ct[slice_idx],
                cmap="gray",
                vmin=all_min,
                vmax=all_max,
                interpolation="nearest",
            )
            ax_gt.axis("off")

            for col_idx, (model_variant, label) in enumerate(MODEL_VARIANTS):
                ax = fig.add_subplot(gs[row_idx + 1, col_idx + 2])
                fake = results[model_variant]["fake"]
                ax.imshow(
                    fake[slice_idx],
                    cmap="gray",
                    vmin=all_min,
                    vmax=all_max,
                    interpolation="nearest",
                )
                ax.axis("off")

        output_file = (
            args.output if args.output else f"{args.tag}_{args.patient_id}_figure.png"
        )

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "comparison_plots")
        os.makedirs(output_dir, exist_ok=True)

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
