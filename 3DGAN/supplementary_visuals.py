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
        "--load_path",
        type=str,
        default=None,
        dest="load_path",
        help="if load_path is not None, model will load from load_path",
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
    - Top-right: xray1 and xray2 (if available) - positioned in corner
    - Below: Ground Truth CT and Generated CT side by side (sampled slices)
    """
    with PdfPages(str(output_path)) as pdf:
        for sample in tqdm(samples, desc="Creating PDF pages"):
            name = sample["name"]
            gt_ct = sample["gt"]
            fake_ct = sample["fake"]
            xray1 = sample.get("xray1")
            xray2 = sample.get("xray2")

            # Determine number of slices to show (every 10th slice)
            step = 10
            depth = gt_ct.shape[0]
            slice_indices = list(range(0, depth, step))
            if len(slice_indices) == 0:
                slice_indices = [depth // 2]
            if len(slice_indices) > 15:
                slice_indices = slice_indices[:15]

            n_slices = len(slice_indices)

            # Layout: CT slices take most of the page, xrays in top-right corner
            # Use GridSpec for precise control
            fig_height = 1 + n_slices * 3.0
            fig = plt.figure(figsize=(14, fig_height))

            # Title at very top
            fig.suptitle(f"Sample: {name}", fontsize=14, fontweight="bold", y=0.98)

            # Create gridspec: top row for xrays (narrow, right portion), rest for CT slices
            gs = fig.add_gridspec(
                nrows=n_slices + 1, ncols=2,
                height_ratios=[0.8] + [1.0] * n_slices,
                width_ratios=[1, 1],
                hspace=0.15, wspace=0.1,
                top=0.93, bottom=0.02, right=0.85
            )

            # X-rays in a narrower box at top-right (columns span full width of right 35%)
            # Create inner gridspec for xrays side by side
            gs_xray = fig.add_gridspec(
                nrows=1, ncols=2,
                wspace=0.05,
                top=0.93, bottom=0.88, left=0.55, right=0.98
            )

            if xray1 is not None:
                ax_x1 = fig.add_subplot(gs_xray[0])
                xray1_display = xray1.squeeze() if xray1.ndim > 2 else xray1
                ax_x1.imshow(xray1_display, cmap="gray", interpolation="nearest")
                ax_x1.set_title("Frontal X-Ray (xray1)", fontsize=10)
                ax_x1.axis('off')
            else:
                ax_x1 = fig.add_subplot(gs_xray[0])
                ax_x1.text(0.5, 0.5, "No Frontal X-Ray", ha='center', va='center')
                ax_x1.axis('off')

            if xray2 is not None:
                ax_x2 = fig.add_subplot(gs_xray[1])
                xray2_display = xray2.squeeze() if xray2.ndim > 2 else xray2
                ax_x2.imshow(xray2_display, cmap="gray", interpolation="nearest")
                ax_x2.set_title("Lateral X-Ray (xray2)", fontsize=10)
                ax_x2.axis('off')
            else:
                ax_x2 = fig.add_subplot(gs_xray[1])
                ax_x2.text(0.5, 0.5, "No Lateral X-Ray", ha='center', va='center')
                ax_x2.axis('off')

            # CT slices: each row has GT (col 0) and Fake (col 1) spanning left 55% of figure
            gs_ct = fig.add_gridspec(
                nrows=n_slices, ncols=2,
                height_ratios=[1.0] * n_slices,
                width_ratios=[1, 1],
                hspace=0.15, wspace=0.08,
                top=0.85, bottom=0.02, left=0.02, right=0.98
            )

            for row_idx, slice_idx in enumerate(slice_indices):
                gt_slice = gt_ct[slice_idx]
                fake_slice = fake_ct[slice_idx]

                # Compute shared vmin/vmax for consistent display
                vmin = min(np.nanmin(gt_slice), np.nanmin(fake_slice))
                vmax = max(np.nanmax(gt_slice), np.nanmax(fake_slice))

                # GT slice (right column)
                ax_gt = fig.add_subplot(gs_ct[row_idx, 1])
                ax_gt.imshow(gt_slice, cmap="gray", vmin=vmin, vmax=vmax, interpolation="nearest")
                ax_gt.set_title(f"GT - Slice {slice_idx}/{depth-1}", fontsize=9)
                ax_gt.axis('off')

                # Fake slice (left column)
                ax_fake = fig.add_subplot(gs_ct[row_idx, 0])
                ax_fake.imshow(fake_slice, cmap="gray", vmin=vmin, vmax=vmax, interpolation="nearest")
                ax_fake.set_title(f"Generated - Slice {slice_idx}/{depth-1}", fontsize=9)
                ax_fake.axis('off')

            pdf.savefig(fig, dpi=150)
            plt.close(fig)


def create_html_visualization(samples, output_dir, checkpoint_num):
    """
    Create per-patient HTML visualizations with:
    - Patient name
    - Xray1 and xray2 images
    - GT and Fake CTs side by side as 3D viewer (slices)
    """
    # Create main output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectory for each patient
    for sample in tqdm(samples, desc="Creating HTML per patient"):
        name = sample["name"]
        gt_ct = sample["gt"]
        fake_ct = sample["fake"]
        xray1 = sample.get("xray1")
        xray2 = sample.get("xray2")

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

        slice_paths_gt = []
        slice_paths_fake = []

        for slice_idx in slice_indices:
            # GT slice
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

            # Fake slice
            fig_fake, ax_fake = plt.subplots(figsize=(4, 4))
            fake_slice = fake_ct[slice_idx]
            vmin = min(vmin, np.nanmin(fake_slice))
            vmax = max(vmax, np.nanmax(fake_slice))
            ax_fake.imshow(fake_slice, cmap="gray", vmin=vmin, vmax=vmax, interpolation="nearest")
            ax_fake.set_title(f"Generated Slice {slice_idx}")
            ax_fake.axis('off')
            fake_path = patient_dir / f"fake_slice_{slice_idx}.png"
            fig_fake.savefig(str(fake_path), dpi=100, bbox_inches='tight')
            plt.close(fig_fake)
            slice_paths_fake.append(fake_path)

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
        .ct-container {{ display: flex; flex-direction: column; align-items: center; gap: 10px; }}
        .ct-row {{ display: flex; justify-content: center; gap: 40px; }}
        .ct-pair {{ text-align: center; }}
        .ct-pair img {{ display: block; margin: 0 auto; border: 1px solid #999; }}
        .slice-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .legend {{ display: flex; justify-content: center; gap: 40px; margin: 10px 0; font-weight: bold; }}
        .legend span {{ padding: 5px 15px; border-radius: 4px; }}
        .legend-gt {{ background-color: #e8f5e9; }}
        .legend-fake {{ background-color: #ffebee; }}
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

    <h2>Computed Tomography (CT) Comparison</h2>
    <div class="legend">
        <span class="legend-gt">Ground Truth (GT)</span>
        <span class="legend-fake">Generated (Fake)</span>
    </div>
    <div class="ct-container">
"""

        for slice_idx in slice_indices:
            gt_path_str = f"gt_slice_{slice_idx}.png"
            fake_path_str = f"fake_slice_{slice_idx}.png"
            html_content += f"""        <div class="ct-row">
            <div class="ct-pair">
                <img src="{fake_path_str}" alt="Fake Slice {slice_idx}">
                <div class="slice-label">Generated - Slice {slice_idx}</div>
            </div>
            <div class="ct-pair">
                <img src="{gt_path_str}" alt="GT Slice {slice_idx}">
                <div class="slice-label">GT - Slice {slice_idx}</div>
            </div>
        </div>
"""

        html_content += """    </div>
    <div class="metadata">
        <p>Generated by supplementary_visuals.py | AECT-GAN 3DGAN</p>
    </div>
</body>
</html>
"""

        html_path = patient_dir / f"{name}.html"
        with open(str(html_path), 'w') as f:
            f.write(html_content)


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

    # Get model
    gan_model = get_model(opt.model_class)()
    print("Model --{}-- will be Used".format(gan_model.name))

    # Set to test
    gan_model.eval()
    gan_model.init_process(opt)
    total_steps, epoch_count = gan_model.setup(opt)

    # Must set to test Mode again
    if "batch" in opt.norm_G:
        gan_model.eval()
    elif "instance" in opt.norm_G:
        gan_model.eval()
        for name, m in gan_model.named_modules():
            if m.__class__.__name__.startswith("InstanceNorm"):
                m.train()
    else:
        raise NotImplementedError()

    # Output directory structure: outputs/supplementary/{data}/{tag}/{datasetfile_stem}/checkpoint_{num}
    dataset_stem = Path(opt.datasetfile).stem if opt.datasetfile else "default"
    result_dir = Path("outputs") / "supplementary" / opt.data / opt.tag / dataset_stem / f"checkpoint_{checkpoint_num}"
    result_dir.mkdir(parents=True, exist_ok=True)

    samples = []
    for epoch_i, data in tqdm(enumerate(dataloader), total=dataset_size, desc="Running inference"):
        if epoch_i >= opt.how_many:
            break

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
        if "std" in opt.dataset_class or "baseline" in opt.dataset_class:
            generate_CT_transpose = generate_CT
            real_CT_transpose = real_CT
        else:
            generate_CT_transpose = np.transpose(generate_CT, (0, 2, 1, 3))
            real_CT_transpose = np.transpose(real_CT, (0, 2, 1, 3))

        generate_CT_transpose = tensor_back_to_unnormalization(
            generate_CT_transpose, opt.CT_MEAN_STD[0], opt.CT_MEAN_STD[1]
        )
        real_CT_transpose = tensor_back_to_unnormalization(
            real_CT_transpose, opt.CT_MEAN_STD[0], opt.CT_MEAN_STD[1]
        )
        generate_CT_transpose = np.clip(generate_CT_transpose, 0, 1)

        # Get xrays from G_input1 and G_input2 (these are the actual xray inputs)
        xray1 = None
        xray2 = None
        if "G_input1" in visuals:
            xray1 = visuals["G_input1"].data.clone().cpu().numpy()[0].astype(np.float32)
            # Unnormalize xrays using XRAY1_MEAN_STD
            if hasattr(opt, 'XRAY1_MEAN_STD') and opt.XRAY1_MEAN_STD is not None:
                xray1 = tensor_back_to_unnormalization(
                    xray1[np.newaxis, ...], opt.XRAY1_MEAN_STD[0], opt.XRAY1_MEAN_STD[1]
                )[0]
            xray1 = np.clip(xray1, 0, 1)

        if "G_input2" in visuals:
            xray2 = visuals["G_input2"].data.clone().cpu().numpy()[0].astype(np.float32)
            if hasattr(opt, 'XRAY2_MEAN_STD') and opt.XRAY2_MEAN_STD is not None:
                xray2 = tensor_back_to_unnormalization(
                    xray2[np.newaxis, ...], opt.XRAY2_MEAN_STD[0], opt.XRAY2_MEAN_STD[1]
                )[0]
            xray2 = np.clip(xray2, 0, 1)

        sample = {
            "name": name,
            "gt": real_CT_transpose[0],
            "fake": generate_CT_transpose[0],
            "xray1": xray1,
            "xray2": xray2,
        }
        samples.append(sample)

        del visuals, img_path

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
