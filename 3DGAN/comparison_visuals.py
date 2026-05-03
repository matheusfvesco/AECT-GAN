# ------------------------------------------------------------------------------
# supplementary_visuals.py
#
# Generates PDF and HTML visualizations for CTGAN inference results.
# Each PDF page shows ground truth CT, generated CT side by side, with
# input xrays (frontal/lateral) in the top-right corner and sample name
# at the top. HTML visualizations are saved in per-patient subdirectories.
# ------------------------------------------------------------------------------

import argparse
from lib.config.config import cfg_from_yaml, cfg, merge_dict_and_yaml, print_easy_dict
from lib.dataset.factory import get_dataset
from lib.model.factory import get_model
from lib.utils.visualizer import tensor_back_to_unnormalization, tensor_back_to_unMinMax
import copy
import tqdm
import torch
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import SimpleITK as sitk
from tqdm import tqdm


def parse_args():
    parse = argparse.ArgumentParser(description="CTGAN Supplementary Visuals")
    parse.add_argument("--data", type=str, default="", dest="data", help="input data ")
    parse.add_argument(
        "--tag", type=str, default="", dest="tag", help="distinct from other try"
    )
    parse.add_argument(
        "--dataroot", type=str, default="", dest="dataroot", help="input data root"
    )
    parse.add_argument(
        "--dataset", type=str, default="", dest="dataset", help="Train or test or valid"
    )
    parse.add_argument(
        "--datasetfile",
        type=str,
        default="",
        dest="datasetfile",
        help="Train or test or valid file path",
    )
    parse.add_argument(
        "--ymlpath",
        type=str,
        default=None,
        dest="ymlpath",
        help="config have been modified",
    )
    parse.add_argument(
        "--gpu", type=str, default="0,1", dest="gpuid", help="gpu is split by ,"
    )
    parse.add_argument(
        "--dataset_class",
        type=str,
        default="unalign",
        dest="dataset_class",
        help="Dataset class should select from unalign /",
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
        help="Root path to model weights directory",
    )
    parse.add_argument(
        "--how_many",
        type=int,
        dest="how_many",
        default=50,
        help="if specified, only run this number of test samples for visualization",
    )
    parse.add_argument(
        "--resultdir", type=str, default="", dest="resultdir", help="dir to save result"
    )
    parse.add_argument(
        "--result_subdir",
        type=str,
        default=None,
        dest="result_subdir",
        help="Override subdirectory name in output path (e.g., 'test' or 'real-test')",
    )
    args = parse.parse_args()
    return args


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


def create_pdf_visualization(samples, output_path, checkpoint_num):
    """
    Create a PDF with each sample on a page showing:
    - Top row: xray1 and xray2 (if available)
    - Second row: GT CT and 4 columns of Generated CTs (one per model variant)
      Columns: d2_multiview2500 | synthetic | real | mixed
    """
    from collections import OrderedDict

    # Group samples by name - each group has 4 variants
    grouped = OrderedDict()
    for sample in samples:
        name = sample["name"]
        if name not in grouped:
            grouped[name] = []
        grouped[name].append(sample)

    # Define column order and labels
    VARIANT_COLS = [
        ("d2_multiview2500", "Model C"),
        ("multiview-GAN-dataset-complete-clipped-shifted", "Model E"),
        ("multiview-GAN-dataset-complete-clipped-shifted-real_mixed", "Model M"),
    ]

    with PdfPages(str(output_path)) as pdf:
        for name, variant_samples in tqdm(grouped.items(), desc="Creating PDF pages"):
            # Build dict keyed by variant for easy access
            by_variant = {s["model_variant"]: s for s in variant_samples}

            # Get common data (same across variants)
            gt_ct = variant_samples[0]["gt"]
            xray1 = variant_samples[0].get("xray1")
            xray2 = variant_samples[0].get("xray2")

            # Determine number of slices to show (every 10th slice)
            step = 10
            depth = gt_ct.shape[0]
            slice_indices = list(range(0, depth, step))
            if len(slice_indices) == 0:
                slice_indices = [depth // 2]
            if len(slice_indices) > 15:
                slice_indices = slice_indices[:15]

            n_slices = len(slice_indices)

            # Layout: xrays at top, then GT + 4 variants per row
            # 5 columns: [GT | d2 | synthetic | real | mixed]
            # n_slices rows of CT slices + 1 row for xrays at top
            fig_height = 2 + n_slices * 2.5
            fig = plt.figure(figsize=(20, fig_height))

            # Title
            fig.suptitle(f"Sample: {name}", fontsize=14, fontweight="bold", y=0.98)

            # X-ray row at top
            gs_xray = fig.add_gridspec(
                nrows=1, ncols=2,
                wspace=0.05,
                top=0.94, bottom=0.88, left=0.02, right=0.98
            )

            if xray1 is not None:
                ax_x1 = fig.add_subplot(gs_xray[0])
                xray1_display = xray1.squeeze() if xray1.ndim > 2 else xray1
                ax_x1.imshow(xray1_display, cmap="gray", interpolation="nearest")
                ax_x1.set_title("Frontal X-Ray", fontsize=10)
                ax_x1.axis('off')
            else:
                ax_x1 = fig.add_subplot(gs_xray[0])
                ax_x1.text(0.5, 0.5, "No Frontal X-Ray", ha='center', va='center')
                ax_x1.axis('off')

            if xray2 is not None:
                ax_x2 = fig.add_subplot(gs_xray[1])
                xray2_display = xray2.squeeze() if xray2.ndim > 2 else xray2
                ax_x2.imshow(xray2_display, cmap="gray", interpolation="nearest")
                ax_x2.set_title("Lateral X-Ray", fontsize=10)
                ax_x2.axis('off')
            else:
                ax_x2 = fig.add_subplot(gs_xray[1])
                ax_x2.text(0.5, 0.5, "No Lateral X-Ray", ha='center', va='center')
                ax_x2.axis('off')

            # CT slices: each row has 4 columns [GT | d2 | synthetic | mixed]
            gs_ct = fig.add_gridspec(
                nrows=n_slices, ncols=4,
                height_ratios=[1.0] * n_slices,
                width_ratios=[1, 1, 1, 1],
                hspace=0.15, wspace=0.05,
                top=0.85, bottom=0.02, left=0.02, right=0.98
            )

            for row_idx, slice_idx in enumerate(slice_indices):
                gt_slice = gt_ct[slice_idx]

                # Get all variant slices and compute shared vmin/vmax
                variant_slices = {}
                all_min = np.nanmin(gt_slice)
                all_max = np.nanmax(gt_slice)
                for variant_key, _ in VARIANT_COLS:
                    if variant_key in by_variant:
                        fake_slice = by_variant[variant_key]["fake"][slice_idx]
                        variant_slices[variant_key] = fake_slice
                        all_min = min(all_min, np.nanmin(fake_slice))
                        all_max = max(all_max, np.nanmax(fake_slice))

                # GT slice (column 0)
                ax_gt = fig.add_subplot(gs_ct[row_idx, 0])
                ax_gt.imshow(gt_slice, cmap="gray", vmin=all_min, vmax=all_max, interpolation="nearest")
                if row_idx == 0:
                    ax_gt.set_title(f"GT", fontsize=9, fontweight="bold")
                ax_gt.axis('off')

                # Variant slices (columns 1-4)
                for col_idx, (variant_key, label) in enumerate(VARIANT_COLS):
                    ax_var = fig.add_subplot(gs_ct[row_idx, col_idx + 1])
                    if variant_key in variant_slices:
                        ax_var.imshow(variant_slices[variant_key], cmap="gray", vmin=all_min, vmax=all_max, interpolation="nearest")
                        if row_idx == 0:
                            ax_var.set_title(f"{label}", fontsize=9)
                    else:
                        ax_var.text(0.5, 0.5, "N/A", ha='center', va='center')
                    ax_var.axis('off')

            pdf.savefig(fig, dpi=150)
            plt.close(fig)


def create_html_visualization(samples, output_dir, checkpoint_num):
    """
    Create per-patient HTML visualizations with:
    - Patient name
    - Xray1 and xray2 images
    - GT CT and 4 columns of Generated CTs (one per model variant)
      Columns: d2_multiview2500 | synthetic | real | mixed
    """
    from collections import OrderedDict

    # Create main output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Group samples by name - each group has 4 variants
    grouped = OrderedDict()
    for sample in samples:
        name = sample["name"]
        if name not in grouped:
            grouped[name] = []
        grouped[name].append(sample)

    # Define column order and labels
    VARIANT_COLS = [
        ("d2_multiview2500", "Model C"),
        ("multiview-GAN-dataset-complete-clipped-shifted", "Model E"),
        ("multiview-GAN-dataset-complete-clipped-shifted-real_mixed", "Model M"),
    ]

    # Create subdirectory for each patient
    for name, variant_samples in tqdm(grouped.items(), desc="Creating HTML per patient"):
        # Build dict keyed by variant for easy access
        by_variant = {s["model_variant"]: s for s in variant_samples}

        # Get common data (same across variants)
        gt_ct = variant_samples[0]["gt"]
        xray1 = variant_samples[0].get("xray1")
        xray2 = variant_samples[0].get("xray2")

        patient_dir = output_dir / name
        patient_dir.mkdir(parents=True, exist_ok=True)

        # Create PNG slices for this patient
        step = 10
        depth = gt_ct.shape[0]
        slice_indices = list(range(0, depth, step))
        if len(slice_indices) == 0:
            slice_indices = [depth // 2]
        if len(slice_indices) > 15:
            slice_indices = slice_indices[:15]

        # GT slice paths
        slice_paths_gt = []
        for slice_idx in slice_indices:
            fig_gt, ax_gt = plt.subplots(figsize=(4, 4))
            gt_slice = gt_ct[slice_idx]
            vmin, vmax = np.nanmin(gt_slice), np.nanmax(gt_slice)
            ax_gt.imshow(gt_slice, cmap="gray", vmin=vmin, vmax=vmax, interpolation="nearest")
            ax_gt.set_title(f"GT Slice {slice_idx}")
            ax_gt.axis('off')
            gt_path = patient_dir / f"gt_slice_{slice_idx}.png"
            fig_gt.savefig(str(gt_path), dpi=100, bbox_inches='tight')
            plt.close(fig_gt)
            slice_paths_gt.append(gt_path)

        # Variant slice paths
        variant_slice_paths = {variant_key: [] for variant_key, _ in VARIANT_COLS}
        for slice_idx in slice_indices:
            # Get all variant slices and compute shared vmin/vmax
            gt_slice = gt_ct[slice_idx]
            all_min = np.nanmin(gt_slice)
            all_max = np.nanmax(gt_slice)
            variant_slices = {}
            for variant_key, _ in VARIANT_COLS:
                if variant_key in by_variant:
                    fake_slice = by_variant[variant_key]["fake"][slice_idx]
                    variant_slices[variant_key] = fake_slice
                    all_min = min(all_min, np.nanmin(fake_slice))
                    all_max = max(all_max, np.nanmax(fake_slice))

            # Save GT slice
            fig, axes = plt.subplots(1, 5, figsize=(20, 4))
            axes[0].imshow(gt_slice, cmap="gray", vmin=all_min, vmax=all_max, interpolation="nearest")
            axes[0].set_title("GT", fontsize=10)
            axes[0].axis('off')

            # Save variant slices
            for col_idx, (variant_key, label) in enumerate(VARIANT_COLS):
                if variant_key in variant_slices:
                    fake_slice = variant_slices[variant_key]
                    variant_path = patient_dir / f"variant_{variant_key}_slice_{slice_idx}.png"
                    fig_v, ax_v = plt.subplots(figsize=(4, 4))
                    ax_v.imshow(fake_slice, cmap="gray", vmin=all_min, vmax=all_max, interpolation="nearest")
                    ax_v.set_title(f"{label}", fontsize=9)
                    ax_v.axis('off')
                    fig_v.savefig(str(variant_path), dpi=100, bbox_inches='tight')
                    plt.close(fig_v)
                    variant_slice_paths[variant_key].append(variant_path)
                else:
                    variant_slice_paths[variant_key].append(None)

            plt.close(fig)

        # Save xray images if available
        xray1_path = None
        xray2_path = None
        if xray1 is not None:
            fig_x1, ax_x1 = plt.subplots(figsize=(6, 6))
            xray1_display = xray1.squeeze() if xray1.ndim > 2 else xray1
            ax_x1.imshow(xray1_display, cmap="gray", interpolation="nearest")
            ax_x1.set_title("Frontal X-Ray (xray1)")
            ax_x1.axis('off')
            xray1_path = patient_dir / "xray1.png"
            fig_x1.savefig(str(xray1_path), dpi=100, bbox_inches='tight')
            plt.close(fig_x1)

        if xray2 is not None:
            fig_x2, ax_x2 = plt.subplots(figsize=(6, 6))
            xray2_display = xray2.squeeze() if xray2.ndim > 2 else xray2
            ax_x2.imshow(xray2_display, cmap="gray", interpolation="nearest")
            ax_x2.set_title("Lateral X-Ray (xray2)")
            ax_x2.axis('off')
            xray2_path = patient_dir / "xray2.png"
            fig_x2.savefig(str(xray2_path), dpi=100, bbox_inches='tight')
            plt.close(fig_x2)

        # Generate HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Patient: {name}</title>
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
        .header-gt {{ background-color: #e8f5e9; }}
        .header-d2 {{ background-color: #e3f2fd; }}
        .header-synth {{ background-color: #fff3e0; }}
        .header-mixed {{ background-color: #e0f7fa; }}
        .metadata {{ color: #777; font-size: 14px; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Patient Visualization: {name}</h1>
    <div class="patient-info">
        <strong>Patient ID:</strong> {name} | <strong>CT Depth:</strong> {depth} slices
    </div>

    <h2>Input X-Rays</h2>
    <div class="xray-container">
"""
        if xray1_path:
            html_content += f'        <div><img src="{xray1_path.name}" alt="Frontal X-Ray"><br><center>Frontal (xray1)</center></div>\n'
        if xray2_path:
            html_content += f'        <div><img src="{xray2_path.name}" alt="Lateral X-Ray"><br><center>Lateral (xray2)</center></div>\n'
        if xray1_path is None and xray2_path is None:
            html_content += "        <p>No x-ray images available for this sample.</p>\n"

        html_content += """    </div>

    <h2>CT Comparison: GT vs Generated from 4 Model Variants</h2>
    <div class="ct-table">
"""
        for slice_idx in slice_indices:
            gt_path_str = f"gt_slice_{slice_idx}.png"
            html_content += f"""        <div class="ct-row">
            <div class="ct-col">
                <div class="col-header header-gt">GT</div>
                <img src="{gt_path_str}" alt="GT Slice {slice_idx}">
                <div class="slice-label">Slice {slice_idx}</div>
            </div>
"""
            for variant_key, label in VARIANT_COLS:
                variant_path = variant_slice_paths[variant_key][slice_indices.index(slice_idx)]
                if variant_path is not None:
                    html_content += f"""            <div class="ct-col">
                <div class="col-header header-{variant_key[:6]}">{label}</div>
                <img src="{variant_path.name}" alt="{label} Slice {slice_idx}">
                <div class="slice-label">Slice {slice_idx}</div>
            </div>
"""
            html_content += "        </div>\n"

        html_content += """    </div>
    <div class="metadata">
        <p>Generated by comparison_visuals.py | AECT-GAN 3DGAN</p>
    </div>
</body>
</html>
"""

        html_path = patient_dir / f"{name}.html"
        with open(str(html_path), 'w') as f:
            f.write(html_content)


def run_inference_single(model_variant, model_root, data, opt):
    """
    Loads model weights for a given variant and runs inference on a single sample.
    Model is loaded fresh on each call and unloaded when function returns.

    Args:
        model_variant: e.g. "d2_multiview2500"
        model_root: root path to model weights
        data: a single data sample from the dataloader
        opt: pre-initialized config object (all params same across variants)

    Returns:
        sample: dict with 'name', 'gt', 'fake', 'xray1', 'xray2'
    """
    # Build load_path
    load_path = f"{model_root.rstrip('/')}/{model_variant}/checkpoint"

    # Just override load_path - rest of config comes from pre-built opt
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

    # Run inference on single sample
    gan_model.set_input(data)
    gan_model.test()

    visuals = gan_model.get_current_visuals()
    img_path = gan_model.get_image_paths()

    # Extract sample name
    name1 = os.path.splitext(os.path.basename(img_path[0][0]))[0]
    name2 = os.path.split(os.path.dirname(img_path[0][0]))[-1]
    name = name2 + "_" + name1

    # Get CTs
    generate_CT = visuals["G_fake"].data.clone().cpu().numpy()
    real_CT = visuals["G_real"].data.clone().cpu().numpy()

    # Transpose and unnormalize
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

    # Get xrays
    xray1 = None
    xray2 = None
    if "G_input1" in visuals:
        xray1 = visuals["G_input1"].data.clone().cpu().numpy()[0].astype(np.float32)
        if hasattr(opt_variant, 'XRAY1_MEAN_STD') and opt_variant.XRAY1_MEAN_STD is not None:
            xray1 = tensor_back_to_unnormalization(
                xray1[np.newaxis, ...], opt_variant.XRAY1_MEAN_STD[0], opt_variant.XRAY1_MEAN_STD[1]
            )[0]
        xray1 = np.clip(xray1, 0, 1)

    if "G_input2" in visuals:
        xray2 = visuals["G_input2"].data.clone().cpu().numpy()[0].astype(np.float32)
        if hasattr(opt_variant, 'XRAY2_MEAN_STD') and opt_variant.XRAY2_MEAN_STD is not None:
            xray2 = tensor_back_to_unnormalization(
                xray2[np.newaxis, ...], opt_variant.XRAY2_MEAN_STD[0], opt_variant.XRAY2_MEAN_STD[1]
            )[0]
        xray2 = np.clip(xray2, 0, 1)

    sample = {
        "name": name,
        "gt": real_CT_transpose[0],
        "fake": generate_CT_transpose[0],
        "xray1": xray1,
        "xray2": xray2,
        "model_variant": model_variant,
    }

    del gan_model, visuals, img_path
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return sample


def generate_visualizations(args):
    # List of model variants to iterate over
    MODEL_VARIANTS = [
        "d2_multiview2500",
        "multiview-GAN-dataset-complete-clipped-shifted",
        "multiview-GAN-dataset-complete-clipped-shifted-real_mixed",
    ]

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
    # Merge config with argparse
    opt = copy.deepcopy(cfg)
    opt = merge_dict_and_yaml(args.__dict__, opt)
    print_easy_dict(opt)

    opt.serial_batches = True

    # Add data_augmentation
    datasetClass, _, dataTestClass, collateClass = get_dataset(opt.dataset_class)
    opt.data_augmentation = dataTestClass

    # Get dataset
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

    # Output directory structure: outputs/supplementary/{data}/{tag}/{subdir}/checkpoint_{num}
    if opt.result_subdir:
        subdir = opt.result_subdir
    else:
        subdir = Path(opt.datasetfile).stem if opt.datasetfile else "default"
    result_dir = Path("outputs") / "supplementary" / opt.data / opt.tag / subdir / f"checkpoint_{checkpoint_num}"
    result_dir.mkdir(parents=True, exist_ok=True)

    samples = []
    for epoch_i, data in tqdm(enumerate(dataloader), total=dataset_size, desc="Running inference"):
        if epoch_i >= opt.how_many:
            break

        # For each sample, run inference with all model variants
        for model_variant in MODEL_VARIANTS:
            sample = run_inference_single(
                model_variant=model_variant,
                model_root=args.model_root,
                data=data,
                opt=opt,
            )
            samples.append(sample)

    # Create PDF
    print("Creating PDF visualization...")
    pdf_path = result_dir / f"supplementary_visuals_{checkpoint_num}.pdf"
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
