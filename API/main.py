import base64
import cv2
import numpy as np

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pathlib import Path
from uuid import uuid4
import shutil
import zipfile
from src.core.services import process, predict

app = FastAPI(title="X2CT API", version="1.0")


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
        "message": "X2CT API is running",
        "version": "1.0",
        "endpoints": ["/", "/predict"],
    }


@app.post("/predict")
async def upload_zip(
    file: UploadFile = File(...),
    model_type: str = Form("real"),
):
    # Validate model_type
    if model_type not in ("real", "synthetic", "mixed", "x2ct"):
        raise HTTPException(
            status_code=400,
            detail="model_type must be 'real', 'synthetic', 'mixed', or 'x2ct'"
        )

    # 1. Validate file
    validate_upload(file)

    # 2. Setup paths
    uid = str(uuid4())
    target_dir = get_base_dir() / "uploads" / uid
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 3. Save
        zip_path = await save_upload(file, target_dir)

        # 4. Unzip
        unzip_file(zip_path, target_dir)

        # 5. Process
        ct_arr, frontal_arr, lateral_arr = process(target_dir)

        # 6. Predict - now returns (results, ct_generated, ct_original)
        results, ct_generated, ct_original = predict(
            ct_arr, frontal_arr, lateral_arr, model_type=model_type
        )

        # 7. Serialize everything to base64
        generated_slices = _ct_to_base64_slices(ct_generated.squeeze(0))
        original_slices = _ct_to_base64_slices(ct_original.squeeze(0))

        # 8. Cleanup immediately after processing
        cleanup(target_dir)

        return JSONResponse(
            {
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
            }
        )

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
