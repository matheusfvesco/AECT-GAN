import os
from pathlib import Path
from fastapi import HTTPException
from .dicom import (
    DicomDirectory,
    MultiviewXRayDirectory,
    SingleViewXRayDirectory,
    CTScanDirectory,
)
from .preprocess import CTProcessor
import numpy as np


def process(target_dir: Path):
    """Business logic for processing data."""
    num_dicom_dirs = 0
    dcm_dirs_paths = []
    for dirpath, _, filenames in os.walk(target_dir):
        #print(f"Processing directory: {dirpath}")
        if not filenames:
            continue
        if any(f.lower().endswith(".dcm") for f in filenames):
            num_dicom_dirs += 1
            dcm_dirs_paths.append(dirpath)

    if not dcm_dirs_paths:
        raise HTTPException(
            status_code=400, detail="No DICOM files found in the uploaded zip"
        )
    if num_dicom_dirs > 3:
        raise HTTPException(
            status_code=400,
            detail="Too many DICOM directories found. Please upload a zip with 3 or fewer DICOM directories.",
        )
    num_dcms = [
        len([f for f in os.listdir(dcm_dir) if f.lower().endswith(".dcm")])
        for dcm_dir in dcm_dirs_paths
    ]
    if sum(1 for count in num_dcms if count > 10) > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple DICOM directories with more than 10 DICOM files found. Please upload a zip with only one CT scan (one DICOM directory with more than 10 DICOM files).",
        )
    if sum(1 for count in num_dcms if 1 < count < 10) > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple DICOM directories with more than 1 view found. Please upload a zip with only one multiview X-ray scan or two single-view X-ray scans",
        )

    dcms = []
    for dicom_dir in dcm_dirs_paths:
        dcms.append(DicomDirectory(dicom_dir))
    singleviews: list[SingleViewXRayDirectory] = []
    ct_scan = None
    multiview_xray = None
    for dcm in dcms:
        if isinstance(dcm, CTScanDirectory):
            ct_scan = dcm
        elif isinstance(dcm, MultiviewXRayDirectory):
            multiview_xray = dcm
        elif isinstance(dcm, SingleViewXRayDirectory):
            singleviews.append(dcm)
    if len(singleviews) > 2:
        raise HTTPException(
            status_code=400,
            detail="Too many single-view X-ray directories found. Please upload a zip with 2 or fewer single-view X-ray directories.",
        )
    if singleviews and multiview_xray is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot have both single-view and multiview X-ray directories. Please upload a zip with either one multiview X-ray directory or up to two single-view X-ray directories.",
        )
    if ct_scan is None:
        raise HTTPException(
            status_code=400,
            detail="No CT scan found. Please upload a zip with one CT scan.",
        )
    if not multiview_xray.has_both_views:
        raise HTTPException(
            status_code=400,
            detail="Multiview X-ray directory must contain both frontal and lateral views.",
        )

    ct_arr = ct_scan.get_array()
    ct_processor = CTProcessor(ct_arr, ct_scan)
    ct_processor._transpose()
    ct_processor._resize()
    ct_arr = ct_processor.array

    if multiview_xray is not None:
        frontal_view = multiview_xray.get_by_view_type("frontal")
        lateral_view = multiview_xray.get_by_view_type("lateral")
        frontal_arr = frontal_view.get_array()
        lateral_arr = lateral_view.get_array()
    elif singleviews:
        if len(singleviews) < 2:
            raise HTTPException(
                status_code=400,
                detail="Only one single-view X-ray directory found. Please upload a zip with either one multiview X-ray directory or two single-view X-ray directories.",
            )
        if len(singleviews) > 2:
            raise HTTPException(
                status_code=400,
                detail="Too many single-view X-ray directories found. Please upload a zip with 2 or fewer single-view X-ray directories.",
            )
        for view in singleviews:
            view_obj = view.get_view()
            view_type = view_obj.get_view_type()

            if view_type is None:
                raise HTTPException(
                    status_code=400,
                    detail="Single-view X-ray directory must contain a view with a valid view type (DICOM tag View Position must be AP or PA or LL or RL).",
                )

            if view_type == "frontal":
                frontal_arr = view_obj.get_array()
            elif view_type == "lateral":
                lateral_arr = view_obj.get_array()

    #if not ct_arr or not frontal_arr or not lateral_arr:
    #    raise HTTPException(
    #        status_code=400,
    #        detail="Missing required data. Please ensure the uploaded zip contains one CT scan and either one multiview X-ray scan with both frontal and lateral views or two single-view X-ray scans with one frontal and one lateral view.",
    #    )

    # Clear all caches before returning
    _clear_all_caches(ct_scan)
    if multiview_xray is not None:
        _clear_all_caches(multiview_xray)
    for view in singleviews:
        _clear_all_caches(view)

    return ct_arr, frontal_arr, lateral_arr


def _clear_all_caches(dcm_dir):
    """Recursively clear all caches from a directory and its contents."""
    # Clear directory cache
    if hasattr(dcm_dir, 'cache') and dcm_dir.cache:
        dcm_dir.cache.clear()

    # Clear individual file caches and unload dicoms
    for dcm_file in dcm_dir:
        if hasattr(dcm_file, 'cache') and dcm_file.cache:
            dcm_file.cache.clear()
        if hasattr(dcm_file, '_unload_dicom'):
            dcm_file._unload_dicom()

    if hasattr(dcm_dir, '_unload_dicom'):
        dcm_dir._unload_dicom()


import torch
from .metrics import (
    tensor_back_to_unnormalization,
    tensor_back_to_unMinMax,
    MAE,
    MSE,
    Peak_Signal_to_Noise_Rate_3D,
    Structural_Similarity,
    Cosine_Similarity,
)
import scipy.ndimage as ndimage
import torch.nn as nn
import functools


def preprocess_xray(
    xray_arr: np.ndarray, target_size=(1, 128, 128), min_val=0, max_val=255
) -> torch.Tensor:
    if len(xray_arr.shape) == 2:
        img = np.expand_dims(xray_arr, 0)
    else:
        img = xray_arr
    z, y, x = img.shape
    ori_shape = np.array((z, y, x), dtype=np.float32)
    target = np.array(target_size, dtype=np.float32)
    resize_factor = target / ori_shape
    img_resized = ndimage.zoom(img, resize_factor, order=1)
    img_norm = np.round((img_resized - min_val) / float(max_val - min_val), 6)
    tensor_img = torch.from_numpy(img_norm.astype(np.float32))
    return tensor_img


def predict(ct_arr: np.ndarray, frontal_arr: np.ndarray, lateral_arr: np.ndarray, model_type: str = "real"):
    """
    Business logic for prediction.

    Args:
        ct_arr: Ground truth CT array
        frontal_arr: Frontal X-ray array
        lateral_arr: Lateral X-ray array
        model_type: 'real' or 'synthetic' - which model weights to use
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # Select weight file based on model type
    weight_filename = f"90_net_G_{model_type}.pth"
    weight_path = os.path.join("API", "weights", weight_filename)
    print(f"[DEBUG] Loading model weights from: {weight_path}")

    # 1. Preprocess X-rays
    xray1_tensor = (
        preprocess_xray(frontal_arr).unsqueeze(0).to(device)
    )  # Shape [1, 1, 128, 128]
    xray2_tensor = preprocess_xray(lateral_arr).unsqueeze(0).to(device)

    # 2. Preprocess CT data for metrics
    # The models in test.py expect CT normalized to 0-1 for early metrics, and 0-2500 for later ones.
    # Our generated fake CT comes out in range [-mean/std, ...] which corresponds to mean=0, std=1 in yml
    # So actually fake CT range is around 0.0-1.0
    ct_arr_clipped = np.clip(ct_arr, 0, 2500)
    real_CT_unnorm = (
        ct_arr_clipped / 2500.0
    )  # This matches the 0-1 range array used for ssim/cos is test.py
    # Add batch to unnorm shape => [1, D, H, W]
    real_CT_unnorm_b = np.expand_dims(real_CT_unnorm, 0)

    # 3. Model Architecture & Weights
    # Get Multiview generator initialized with specs from d2_multiview2500.yml
    encoder_norm_layer = functools.partial(
        nn.InstanceNorm2d, affine=False, track_running_stats=True
    )
    decoder_norm_layer = functools.partial(
        nn.InstanceNorm3d, affine=False, track_running_stats=True
    )

    # From yml: CTOrder_Xray1: [0, 1, 3, 2, 4], CTOrder_Xray2: [0, 1, 4, 2, 3]
    view1Order = [0, 1, 3, 2, 4]
    view2Order = [0, 1, 4, 2, 3]

    from .model.generator import (
        UNetLike_DownStep5,
        MultiView_UNetLike_DenseDimensionNet,
    )

    view1Model = UNetLike_DownStep5(
        input_shape=128,
        encoder_input_channels=1,
        decoder_output_channels=1,
        decoder_out_activation=nn.ReLU,
        encoder_norm_layer=encoder_norm_layer,
        decoder_norm_layer=decoder_norm_layer,
        upsample_mode="transposed",
        decoder_feature_out=True,
    )

    view2Model = UNetLike_DownStep5(
        input_shape=128,
        encoder_input_channels=1,
        decoder_output_channels=1,
        decoder_out_activation=nn.ReLU,
        encoder_norm_layer=encoder_norm_layer,
        decoder_norm_layer=decoder_norm_layer,
        upsample_mode="transposed",
        decoder_feature_out=True,
    )

    netG = MultiView_UNetLike_DenseDimensionNet(
        view1Model=view1Model,
        view2Model=view2Model,
        view1Order=view1Order,
        view2Order=view2Order,
        backToSub=True,
        decoder_output_channels=1,
        decoder_out_activation=nn.ReLU,
        decoder_block_list=[1, 1, 1, 1, 1, 0],
        decoder_norm_layer=decoder_norm_layer,
        upsample_mode="transposed",
    ).to(device)

    # test.py sets to eval() and manually sets instance norms to train()
    netG.eval()
    for name, m in netG.named_modules():
        if m.__class__.__name__.startswith("InstanceNorm"):
            m.train()

    if os.path.exists(weight_path):
        checkpoint = torch.load(weight_path, map_location=device)
        # Handle "module." prefix if saved by DataParallel
        from collections import OrderedDict

        # The actual model state dict is nested inside checkpoint['state_dict']
        state_dict = checkpoint.get('state_dict', checkpoint)

        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:] if k.startswith("module.") else k
            new_state_dict[name] = v
        netG.load_state_dict(new_state_dict)

    # 4. Inference
    with torch.no_grad():
        _, _, fake_D = netG([xray1_tensor, xray2_tensor])

    fake_CT = torch.squeeze(fake_D, 1).cpu().numpy()  # [B D H W] - shape (1, 128, 128, 128)

    # In std mode from dataset class, arrays are NOT transposed (matching 3DGAN test.py line 218-220)
    # But ground truth CT is 256^3 from API processing while model outputs 128^3
    # So we need to resize ground truth to match model's output size
    generate_CT_unnorm = tensor_back_to_unnormalization(fake_CT, 0.0, 1.0)
    generate_CT_unnorm = np.clip(generate_CT_unnorm, 0, 1)

    # Resize ground truth CT from (1, 256, 256, 256) to (1, 128, 128, 128) to match model output
    resize_factor = (1, 0.5, 0.5, 0.5)  # Only scale spatial dims, not batch
    real_CT_resized = ndimage.zoom(real_CT_unnorm_b, resize_factor, order=1)

    # 6. Metrics Calculation
    mae0 = MAE(real_CT_resized, generate_CT_unnorm, size_average=False)
    mse0 = MSE(real_CT_resized, generate_CT_unnorm, size_average=False)
    cos_sim = Cosine_Similarity(
        real_CT_resized, generate_CT_unnorm, size_average=False
    )
    ssim = Structural_Similarity(
        real_CT_resized, generate_CT_unnorm, size_average=False, PIXEL_MAX=1.0
    )

    generate_CT_full = tensor_back_to_unMinMax(generate_CT_unnorm, 0, 2500).astype(
        np.int32
    )
    real_CT_full = tensor_back_to_unMinMax(real_CT_resized, 0, 2500).astype(np.int32)

    psnr_3d = Peak_Signal_to_Noise_Rate_3D(
        real_CT_full, generate_CT_full, size_average=False, PIXEL_MAX=4095
    )

    results = {
        "MAE": float(mae0[0] if isinstance(mae0, np.ndarray) else mae0),
        "MSE": float(mse0[0] if isinstance(mse0, np.ndarray) else mse0),
        "Cosine_Similarity": float(
            cos_sim[0] if isinstance(cos_sim, np.ndarray) else cos_sim
        ),
        "SSIM": float(ssim[-1][0] if isinstance(ssim, list) else ssim),
        "PSNR_3D": float(psnr_3d[0] if isinstance(psnr_3d, np.ndarray) else psnr_3d),
        "model_type": model_type,
    }

    # Explicitly clean up GPU memory
    del netG
    del xray1_tensor
    del xray2_tensor
    del fake_D
    del fake_CT
    del generate_CT_unnorm
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return results, generate_CT_full, real_CT_resized
