import base64
import cv2
import numpy as np
import scipy.ndimage as ndimage

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from uuid import uuid4
import shutil
import zipfile
from src.core.services import (
    # Existing
    process,
    # Validation
    detect_content_type,
    validate_content_type_for_predict,
    validate_dicom_xray_structure,
    # Loaders
    load_xrays_from_dicom,
    load_xrays_for_predict,
    # Generation
    generate_ct,
    # Evaluation
    evaluate_ct,
)

app = FastAPI(title="AECT-GAN API", version="1.0")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (frontend runs on different port)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_base_dir() -> Path:
    return Path(__file__).resolve().parent


def validate_upload(file: UploadFile):
    accepted_types = [
        "application/zip",
        "application/x-zip-compressed",
        "application/octet-stream",
    ]
    filename = (file.filename or "").lower()
    if file.content_type not in accepted_types and not filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a zip archive")


async def save_upload(file: UploadFile, target_dir: Path) -> Path:
    zip_path = target_dir / "upload.zip"
    with zip_path.open("wb") as f:
        content = await file.read()
        f.write(content)
    return zip_path


def unzip_file(zip_path: Path, target_dir: Path):
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target_dir)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file")
    finally:
        zip_path.unlink(missing_ok=True)


def cleanup(directory: Path):
    """Removes the entire processing directory."""
    shutil.rmtree(directory, ignore_errors=True)


def _ct_to_base64_slices(ct_volume: np.ndarray) -> list[str]:
    """
    Convert a 3D CT volume (D, H, W) to a list of base64-encoded JPEG slices.

    Args:
        ct_volume: 3D numpy array of shape (D, H, W)

    Returns:
        List of base64-encoded JPEG strings, one per slice
    """
    slices = []
    for i in range(ct_volume.shape[0]):
        slice_2d = ct_volume[i]

        # Normalize to 0-255 for JPEG encoding
        min_val = slice_2d.min()
        max_val = slice_2d.max()
        range_val = max_val - min_val if max_val != min_val else 1
        slice_norm = ((slice_2d - min_val) / range_val * 255).astype(np.uint8)

        # Encode as high-quality JPEG
        _, buffer = cv2.imencode('.jpg', slice_norm, [cv2.IMWRITE_JPEG_QUALITY, 90])
        slices.append(base64.b64encode(buffer).decode('utf-8'))

    return slices


def _xray_to_base64(xray: np.ndarray) -> str:
    """
    Convert a 2D X-ray array to a base64-encoded JPEG string.

    Args:
        xray: 2D numpy array of shape (H, W)

    Returns:
        Base64-encoded JPEG string
    """
    min_val = xray.min()
    max_val = xray.max()
    range_val = max_val - min_val if max_val != min_val else 1
    xray_norm = ((xray - min_val) / range_val * 255).astype(np.uint8)
    _, buffer = cv2.imencode('.jpg', xray_norm, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return base64.b64encode(buffer).decode('utf-8')


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AECT-GAN API is running",
        "version": "1.0",
        "endpoints": ["/", "/evaluate", "/predict"],
    }


@app.post("/evaluate")
async def upload_zip_evaluate(
    file: UploadFile = File(...),
    model_type: str = Form("real"),
):
    """
    Evaluate endpoint - requires DICOM files (CT scan + X-rays).
    Validates structure, generates CT, and calculates metrics.
    """
    print("evaluate request received with model_type:", model_type)

    # 1. Validate model_type
    if model_type not in ("real", "synthetic", "mixed"):
        raise HTTPException(
            status_code=400,
            detail="model_type must be 'real', 'synthetic', or 'mixed'"
        )

    # 2. Validate file is zip
    validate_upload(file)

    # 3. Setup paths
    uid = str(uuid4())
    target_dir = get_base_dir() / "uploads" / uid
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 4. Save and unzip
        zip_path = await save_upload(file, target_dir)
        unzip_file(zip_path, target_dir)

        # 5. Validate DICOM structure
        validate_dicom_xray_structure(target_dir)

        # 6. Process CT and X-rays
        ct_arr, frontal_arr, lateral_arr = process(target_dir)

        # 7. Generate CT
        ct_generated = generate_ct(frontal_arr, lateral_arr, model_type)

        # 8. Evaluate (metrics)
        results = evaluate_ct(ct_generated, ct_arr)
        results["model_type"] = model_type

        # 9. Serialize - resize ground truth to match generated CT resolution for fair comparison
        ct_arr_batched = np.expand_dims(ct_arr, 0)  # → (1, D, H, W)
        resize_factor = (1, 0.5, 0.5, 0.5)  # 256→128
        ct_arr_resized = ndimage.zoom(ct_arr_batched, resize_factor, order=1)  # → (1, 128, 128, 128)
        ct_arr_for_serialize = np.squeeze(ct_arr_resized, 0)  # → (128, 128, 128)

        generated_slices = _ct_to_base64_slices(ct_generated.squeeze(0))
        original_slices = _ct_to_base64_slices(ct_arr_for_serialize)

        # 10. Cleanup
        cleanup(target_dir)

        return JSONResponse({
            "status": "ok",
            "metrics": results,
            "xrays": {
                "frontal": _xray_to_base64(frontal_arr),
                "lateral": _xray_to_base64(lateral_arr),
            },
            "ct": {
                "generated": generated_slices,
                "original": original_slices,
            },
            "dimensions": {
                "depth": int(ct_generated.shape[1]),
                "height": int(ct_generated.shape[2]),
                "width": int(ct_generated.shape[3]),
            },
        })

    except HTTPException:
        cleanup(target_dir)
        raise
    except Exception as exc:
        import traceback
        traceback.print_exc()
        cleanup(target_dir)
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")


@app.post("/predict")
async def upload_zip_predict(
    file: UploadFile = File(...),
    model_type: str = Form("real"),
):
    """
    Predict endpoint - accepts ZIP with 2 DICOM X-ray files OR 2 JPEG/PNG images.
    Generates CT without calculating metrics.
    """
    print("predict request received with model_type:", model_type)

    # 1. Validate model_type
    if model_type not in ("real", "synthetic", "mixed"):
        raise HTTPException(
            status_code=400,
            detail="model_type must be 'real', 'synthetic', or 'mixed'"
        )

    # 2. Validate file is zip
    validate_upload(file)

    # 3. Setup paths
    uid = str(uuid4())
    target_dir = get_base_dir() / "uploads" / uid
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 4. Save and unzip
        zip_path = await save_upload(file, target_dir)
        unzip_file(zip_path, target_dir)

        # 5. Validate content type (dicom vs images vs mixed)
        validate_content_type_for_predict(target_dir)

        # 6. Load X-rays (from DICOM or images)
        frontal_arr, lateral_arr = load_xrays_for_predict(target_dir)

        # 7. Generate CT
        ct_generated = generate_ct(frontal_arr, lateral_arr, model_type)

        # 8. Serialize
        generated_slices = _ct_to_base64_slices(ct_generated.squeeze(0))

        # 9. Cleanup
        cleanup(target_dir)

        return JSONResponse({
            "status": "ok",
            "model_type": model_type,
            "xrays": {
                "frontal": _xray_to_base64(frontal_arr),
                "lateral": _xray_to_base64(lateral_arr),
            },
            "ct": {
                "generated": generated_slices,
            },
            "dimensions": {
                "depth": int(ct_generated.shape[1]),
                "height": int(ct_generated.shape[2]),
                "width": int(ct_generated.shape[3]),
            },
        })

    except HTTPException:
        cleanup(target_dir)
        raise
    except Exception as exc:
        import traceback
        traceback.print_exc()
        cleanup(target_dir)
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
