# ------------------------------------------------------------------------------
# indiana_supplementary_visuals.py
#
# Generates PDF and HTML visualizations for CTGAN inference results on Indiana
# University chest X-ray dataset. Each patient has paired frontal/lateral views
# classified by a ResNet18 classifier. The output shows input xrays and
# generated CT volumes (no ground truth available).
# ------------------------------------------------------------------------------

import argparse
import copy
import os
from collections import defaultdict
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


def parse_args():
    parse = argparse.ArgumentParser(description="CTGAN Indiana University X-Ray Supplementary Visuals")
    parse.add_argument("--indiana_dir", type=str, default="data/indiana_png", dest="indiana_dir",
                        help="path to Indiana PNG dataset directory")
    parse.add_argument("--tag", type=str, default="indiana", dest="tag",
                        help="distinct tag for output directory")
    parse.add_argument("--data", type=str, default="indiana", dest="data",
                        help="input data identifier")
    parse.add_argument("--ymlpath", type=str, default=None, dest="ymlpath",
                        help="config yaml path")
    parse.add_argument("--gpu", type=str, default="0,1", dest="gpuid", help="gpu is split by ,")
    parse.add_argument("--dataset_class", type=str, default="align_ct_xray_views_std", dest="dataset_class",
                        help="Dataset class should select from unalign / align_ct_xray_views_std / etc.")
    parse.add_argument("--model_class", type=str, default="cyclegan", dest="model_class",
                        help="Model class should select from cyclegan / ")
    parse.add_argument("--check_point", type=str, default=None, dest="check_point",
                        help="which epoch to load? ")
    parse.add_argument("--latest", action="store_true", dest="latest",
                        help="set to latest to use latest cached model")
    parse.add_argument("--verbose", action="store_true", dest="verbose",
                        help="if specified, print more debugging information")
    parse.add_argument("--load_path", type=str, default=None, dest="load_path",
                        help="if load_path is not None, model will load from load_path")
    parse.add_argument("--how_many", type=int, dest="how_many", default=50,
                        help="if specified, only process this number of patients")
    parse.add_argument("--resultdir", type=str, default="", dest="resultdir",
                        help="dir to save result")
    parse.add_argument("--classifier_weights", type=str,
                        default="save_models/xray_classifier.pth",
                        dest="classifier_weights",
                        help="path to xray classifier weights")
    args = parse.parse_args()
    return args


def group_images_by_patient(indiana_dir):
    """Group images by patient ID from the Indiana PNG dataset."""
    indiana_dir = Path(indiana_dir)
    files = sorted([f for f in os.listdir(indiana_dir) if f.endswith('.png')])

    groups = defaultdict(list)
    for f in files:
        # Extract patient ID from filename
        # Pattern: CXR{num}[_{suffix}]_IM-{id}-{viewcode}.png
        name_without_ext = f.replace('.png', '')
        parts = name_without_ext.split('_')

        if parts[0] == 'CXR':
            # Handle CXR{num} or CXR{num}_{suffix} format
            if len(parts) >= 3 and parts[2] == 'IM':
                # Format: CXR1_1_IM-0001-3001
                patient_id = '_'.join(parts[:2])  # CXR1_1
            elif len(parts) >= 2 and parts[1].startswith('IM'):
                # Format: CXR1_IM-0001-3001 (rare)
                patient_id = parts[0]
            elif len(parts) >= 2 and not parts[1].startswith('IM'):
                # Format: CXR1_1_IM-0001-3001
                patient_id = '_'.join(parts[:2])
            else:
                patient_id = parts[0]
        else:
            patient_id = parts[0]

        groups[patient_id].append(indiana_dir / f)

    return groups


def classify_and_pair_images(patient_groups, classifier_weights, fine_size=128):
    """
    Classify each image as frontal or lateral and pair them per patient.
    Returns list of dicts: {'patient_id': str, 'frontal': PIL.Image, 'lateral': PIL.Image}
    """
    paired_samples = []

    for patient_id, image_paths in tqdm(patient_groups.items(), desc="Classifying views"):
        if len(image_paths) < 2:
            # Skip patients with fewer than 2 images
            continue

        # Load all images for this patient
        patient_images = []
        for img_path in image_paths:
            try:
                img = Image.open(img_path).convert('L')  # Convert to grayscale
                # Resize to fine_size x fine_size
                img = img.resize((fine_size, fine_size), Image.LANCZOS)
                img_arr = np.array(img).astype(np.float32) / 255.0
                patient_images.append({
                    'path': img_path,
                    'array': img_arr
                })
            except Exception as e:
                print(f"Error loading {img_path}: {e}")
                continue

        if len(patient_images) < 2:
            continue

        # Classify each image
        frontal_images = []
        lateral_images = []

        for img_data in patient_images:
            try:
                view_type = classify_xray_view(img_data['array'], weights_path=classifier_weights)
                img_data['view'] = view_type
                if view_type == 'frontal':
                    frontal_images.append(img_data)
                else:
                    lateral_images.append(img_data)
            except Exception as e:
                print(f"Error classifying {img_data['path']}: {e}")
                continue

        # Pair one frontal with one lateral if available
        if frontal_images and lateral_images:
            # Use the first available pair
            paired_samples.append({
                'patient_id': patient_id,
                'frontal': frontal_images[0],
                'lateral': lateral_images[0]
            })
        elif len(frontal_images) >= 2:
            # Use two different frontal views as frontal/lateral substitute
            paired_samples.append({
                'patient_id': patient_id,
                'frontal': frontal_images[0],
                'lateral': frontal_images[1],
                'note': 'both_frontal'
            })
        elif len(lateral_images) >= 2:
            paired_samples.append({
                'patient_id': patient_id,
                'frontal': lateral_images[0],
                'lateral': lateral_images[1],
                'note': 'both_lateral'
            })

    return paired_samples


def prepare_xray_tensors(frontal_img, lateral_img, opt):
    """
    Prepare xray tensors for model input.
    Returns: (ct_tensor, xray_tuple, paths)
    """
    fine_size = opt.fINE_SIZE if hasattr(opt, 'fINE_SIZE') else 128

    # Normalize xrays using the same normalization as training
    # XRAY1_MEAN_STD and XRAY2_MEAN_STD are [0., 1.] in the config, so no actual normalization needed
    frontal_tensor = torch.from_numpy(frontal_img).unsqueeze(0).unsqueeze(0)  # 1x1xHxW
    lateral_tensor = torch.from_numpy(lateral_img).unsqueeze(0).unsqueeze(0)  # 1x1xHxW

    # If MIN_MAX normalization is specified
    if hasattr(opt, 'XRAY1_MIN_MAX') and opt.XRAY1_MIN_MAX is not None:
        xmin, xmax = opt.XRAY1_MIN_MAX
        frontal_tensor = (frontal_tensor - xmin) / (xmax - xmin) if xmax != xmin else frontal_tensor

    if hasattr(opt, 'XRAY2_MIN_MAX') and opt.XRAY2_MIN_MAX is not None:
        xmin, xmax = opt.XRAY2_MIN_MAX
        lateral_tensor = (lateral_tensor - xmin) / (xmax - xmin) if xmax != xmin else lateral_tensor

    # Create dummy CT tensor (the model doesn't use it for inference)
    ct_tensor = torch.zeros(1, 1, 128, 128, 128)

    # Paths for the two xrays
    paths = (
        [str(frontal_img.get('path', 'frontal'))],
        [str(lateral_img.get('path', 'lateral'))]
    )

    return ct_tensor, (frontal_tensor, lateral_tensor), paths


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
    - Top-right: frontal and lateral xrays
    - Below: Generated CT slices
    """
    with PdfPages(str(output_path)) as pdf:
        for sample in tqdm(samples, desc="Creating PDF pages"):
            name = sample["name"]
            fake_ct = sample["fake"]
            frontal_xray = sample.get("frontal")
            lateral_xray = sample.get("lateral")
            note = sample.get("note")

            # Determine number of slices to show (every 10th slice)
            step = 10
            depth = fake_ct.shape[0]
            slice_indices = list(range(0, depth, step))
            if len(slice_indices) == 0:
                slice_indices = [depth // 2]
            if len(slice_indices) > 15:
                slice_indices = slice_indices[:15]

            n_slices = len(slice_indices)

            # Layout: CT slices take most of the page, xrays in top-right corner
            fig_height = 1 + n_slices * 3.0
            fig = plt.figure(figsize=(14, fig_height))

            # Title at very top
            title_str = f"Sample: {name}"
            if note:
                title_str += f" ({note})"
            fig.suptitle(title_str, fontsize=14, fontweight="bold", y=0.98)

            # Create gridspec: top row for xrays (narrow, right portion), rest for CT slices
            gs = fig.add_gridspec(
                nrows=n_slices + 1, ncols=2,
                height_ratios=[0.8] + [1.0] * n_slices,
                width_ratios=[1, 1],
                hspace=0.15, wspace=0.1,
                top=0.93, bottom=0.02, right=0.85
            )

            # X-rays in a narrower box at top-right
            gs_xray = fig.add_gridspec(
                nrows=1, ncols=2,
                wspace=0.05,
                top=0.93, bottom=0.88, left=0.55, right=0.98
            )

            if frontal_xray is not None:
                ax_x1 = fig.add_subplot(gs_xray[0])
                xray1_display = frontal_xray.squeeze() if frontal_xray.ndim > 2 else frontal_xray
                ax_x1.imshow(xray1_display, cmap="gray", interpolation="nearest")
                ax_x1.set_title("Frontal X-Ray", fontsize=10)
                ax_x1.axis('off')
            else:
                ax_x1 = fig.add_subplot(gs_xray[0])
                ax_x1.text(0.5, 0.5, "No Frontal X-Ray", ha='center', va='center')
                ax_x1.axis('off')

            if lateral_xray is not None:
                ax_x2 = fig.add_subplot(gs_xray[1])
                xray2_display = lateral_xray.squeeze() if lateral_xray.ndim > 2 else lateral_xray
                ax_x2.imshow(xray2_display, cmap="gray", interpolation="nearest")
                ax_x2.set_title("Lateral X-Ray", fontsize=10)
                ax_x2.axis('off')
            else:
                ax_x2 = fig.add_subplot(gs_xray[1])
                ax_x2.text(0.5, 0.5, "No Lateral X-Ray", ha='center', va='center')
                ax_x2.axis('off')

            # CT slices: each row has Generated CT
            gs_ct = fig.add_gridspec(
                nrows=n_slices, ncols=1,
                hspace=0.15, wspace=0.08,
                top=0.85, bottom=0.02, left=0.02, right=0.98
            )

            for row_idx, slice_idx in enumerate(slice_indices):
                fake_slice = fake_ct[slice_idx]

                # Generated slice
                ax_fake = fig.add_subplot(gs_ct[row_idx, 0])
                vmin, vmax = np.nanmin(fake_slice), np.nanmax(fake_slice)
                ax_fake.imshow(fake_slice, cmap="gray", vmin=vmin, vmax=vmax,
                               interpolation="nearest")
                ax_fake.set_title(f"Generated CT - Slice {slice_idx}/{depth-1}", fontsize=9)
                ax_fake.axis('off')

            pdf.savefig(fig, dpi=150)
            plt.close(fig)


def create_html_visualization(samples, output_dir, checkpoint_num):
    """
    Create per-patient HTML visualizations with:
    - Patient name
    - Frontal and lateral xray images
    - Generated CT slices
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for sample in tqdm(samples, desc="Creating HTML per patient"):
        name = sample["name"]
        fake_ct = sample["fake"]
        frontal_xray = sample.get("frontal")
        lateral_xray = sample.get("lateral")
        note = sample.get("note")

        patient_dir = output_dir / name
        patient_dir.mkdir(parents=True, exist_ok=True)

        # Create PNG slices for this patient
        step = 10
        depth = fake_ct.shape[0]
        slice_indices = list(range(0, depth, step))
        if len(slice_indices) == 0:
            slice_indices = [depth // 2]
        if len(slice_indices) > 15:
            slice_indices = slice_indices[:15]

        slice_paths_fake = []

        for slice_idx in slice_indices:
            fig_fake, ax_fake = plt.subplots(figsize=(4, 4))
            fake_slice = fake_ct[slice_idx]
            vmin, vmax = np.nanmin(fake_slice), np.nanmax(fake_slice)
            ax_fake.imshow(fake_slice, cmap="gray", vmin=vmin, vmax=vmax,
                           interpolation="nearest")
            ax_fake.set_title(f"Generated CT - Slice {slice_idx}")
            ax_fake.axis('off')
            fake_path = patient_dir / f"fake_slice_{slice_idx}.png"
            fig_fake.savefig(str(fake_path), dpi=100, bbox_inches='tight')
            plt.close(fig_fake)
            slice_paths_fake.append(fake_path)

        # Save xray images if available
        frontal_path = None
        lateral_path = None

        if frontal_xray is not None:
            fig_x1, ax_x1 = plt.subplots(figsize=(6, 6))
            xray1_display = frontal_xray.squeeze() if frontal_xray.ndim > 2 else frontal_xray
            ax_x1.imshow(xray1_display, cmap="gray", interpolation="nearest")
            ax_x1.set_title("Frontal X-Ray")
            ax_x1.axis('off')
            frontal_path = patient_dir / "frontal.png"
            fig_x1.savefig(str(frontal_path), dpi=100, bbox_inches='tight')
            plt.close(fig_x1)

        if lateral_xray is not None:
            fig_x2, ax_x2 = plt.subplots(figsize=(6, 6))
            xray2_display = lateral_xray.squeeze() if lateral_xray.ndim > 2 else lateral_xray
            ax_x2.imshow(xray2_display, cmap="gray", interpolation="nearest")
            ax_x2.set_title("Lateral X-Ray")
            ax_x2.axis('off')
            lateral_path = patient_dir / "lateral.png"
            fig_x2.savefig(str(lateral_path), dpi=100, bbox_inches='tight')
            plt.close(fig_x2)

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
        .ct-container {{ display: flex; flex-direction: column; align-items: center; gap: 10px; }}
        .ct-row {{ display: flex; justify-content: center; }}
        .ct-pair {{ text-align: center; }}
        .ct-pair img {{ display: block; margin: 0 auto; border: 1px solid #999; }}
        .slice-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
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
            html_content += "        <p>No x-ray images available for this sample.</p>\n"

        html_content += """    </div>

    <h2>Generated Computed Tomography (CT)</h2>
    <div class="ct-container">
"""

        for slice_idx in slice_indices:
            fake_path_str = f"fake_slice_{slice_idx}.png"
            html_content += f"""        <div class="ct-row">
            <div class="ct-pair">
                <img src="{fake_path_str}" alt="Generated Slice {slice_idx}">
                <div class="slice-label">Generated - Slice {slice_idx}</div>
            </div>
        </div>
"""

        html_content += """    </div>
    <div class="metadata">
        <p>Generated by indiana_supplementary_visuals.py | AECT-GAN 3DGAN</p>
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
    else:
        # Use default config for multiview2500
        default_yml = os.path.join(script_dir, "experiment", "multiview2500", "d2_multiview2500.yml")
        if os.path.exists(default_yml):
            cfg_from_yaml(default_yml)

    # Merge config with argparse
    opt = copy.deepcopy(cfg)
    opt = merge_dict_and_yaml(args.__dict__, opt)
    print_easy_dict(opt)

    opt.serial_batches = True

    # Get fine_size from DATA_AUG config (default to 128)
    fine_size = opt.DATA_AUG.fine_size if hasattr(opt, 'DATA_AUG') and hasattr(opt.DATA_AUG, 'fine_size') else 128

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
        patients_with_2plus = dict(list(patients_with_2plus.items())[:args.how_many])
        print(f"Limited to first {args.how_many} patients for classification")

    # Classify and pair images
    print("Classifying and pairing images...")
    paired_samples = classify_and_pair_images(
        patients_with_2plus,
        args.classifier_weights,
        fine_size=fine_size
    )
    print(f"Found {len(paired_samples)} patients with valid pairs")

    if len(paired_samples) == 0:
        print("No valid patient pairs found. Exiting.")
        return []

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

    # Output directory - include model name from load_path if available
    # Structure: outputs/supplementary/data/<author>/<project>/<model_name>/<indiana|tag>/checkpoint_<num>/
    if args.load_path:
        # Extract model name from load_path (e.g., multiview-GAN-dataset-complete-clipped-shifted-real_mixed)
        load_path_obj = Path(args.load_path)
        model_name = load_path_obj.parent.name  # e.g., multiview-GAN-dataset-complete-clipped-shifted-real_mixed

        # args.data is like "data/chengsq/AECT-GAN/model_dic/MultiView-AECT-GAN"
        # We want to strip the leading "data/" and use the rest
        data_path = Path(args.data)
        if data_path.parts[0] == 'data':
            data_path = Path(*data_path.parts[1:])  # Remove leading 'data'

        result_dir = Path("outputs") / "supplementary" / "data" / data_path / model_name / "indiana" / f"checkpoint_{checkpoint_num}"
    else:
        result_dir = Path("outputs") / "supplementary" / "data" / args.data / "indiana" / f"checkpoint_{checkpoint_num}"
    result_dir.mkdir(parents=True, exist_ok=True)

    samples = []
    for patient_data in tqdm(paired_samples, desc="Running inference"):
        try:
            # Prepare input tensors
            frontal_arr = patient_data['frontal']['array']
            lateral_arr = patient_data['lateral']['array']

            # Create input dict for model
            # The model expects: (CT, (xray1, xray2), paths)
            # CT should be 4D (B, D, H, W) - shape (1, 128, 128, 128)
            ct_tensor = torch.zeros(1, 128, 128, 128)

            # Prepare xray tensors with proper normalization
            frontal_tensor = torch.from_numpy(frontal_arr).unsqueeze(0).unsqueeze(0)  # 1x1xHxW
            lateral_tensor = torch.from_numpy(lateral_arr).unsqueeze(0).unsqueeze(0)  # 1x1xHxW

            # Apply min-max normalization if specified in config
            if hasattr(opt, 'XRAY1_MIN_MAX') and opt.XRAY1_MIN_MAX is not None:
                xmin, xmax = opt.XRAY1_MIN_MAX
                if xmax != xmin:
                    frontal_tensor = (frontal_tensor - xmin) / (xmax - xmin)

            if hasattr(opt, 'XRAY2_MIN_MAX') and opt.XRAY2_MIN_MAX is not None:
                xmin, xmax = opt.XRAY2_MIN_MAX
                if xmax != xmin:
                    lateral_tensor = (lateral_tensor - xmin) / (xmax - xmin)

            # Clamp to [0, 1]
            frontal_tensor = torch.clamp(frontal_tensor, 0, 1)
            lateral_tensor = torch.clamp(lateral_tensor, 0, 1)

            xray_tuple = (frontal_tensor, lateral_tensor)

            # Create paths
            frontal_path = str(patient_data['frontal']['path'])
            lateral_path = str(patient_data['lateral']['path'])

            # Set input to model using set_input format expected by Mul_AECT_GAN
            # Format: (CT_tensor, (xray1, xray2), path1, path2)
            gan_model.set_input((ct_tensor, (frontal_tensor, lateral_tensor), frontal_path, lateral_path))

            # Run forward pass - use test mode
            gan_model.test()

            # Get visuals
            visuals = gan_model.get_current_visuals()

            # Get generated CT
            generate_CT = visuals["G_fake"].data.clone().cpu().numpy()

            # Transpose and unnormalize
            if "std" in opt.dataset_class or "baseline" in opt.dataset_class:
                generate_CT_transpose = generate_CT
            else:
                generate_CT_transpose = np.transpose(generate_CT, (0, 2, 1, 3))

            generate_CT_transpose = tensor_back_to_unnormalization(
                generate_CT_transpose, opt.CT_MEAN_STD[0], opt.CT_MEAN_STD[1]
            )
            generate_CT_transpose = np.clip(generate_CT_transpose, 0, 1)

            sample = {
                "name": patient_data['patient_id'],
                "fake": generate_CT_transpose[0],
                "frontal": frontal_arr,
                "lateral": lateral_arr,
                "note": patient_data.get('note'),
            }
            samples.append(sample)

            del visuals

        except Exception as e:
            print(f"Error processing {patient_data['patient_id']}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Create PDF
    print("Creating PDF visualization...")
    pdf_path = result_dir / f"indiana_supplementary_visuals_{checkpoint_num}.pdf"
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
