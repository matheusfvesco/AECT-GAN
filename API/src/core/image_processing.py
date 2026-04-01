"""Image loading and view classification for JPEG/PNG X-rays."""

import os
import cv2
import numpy as np
from pathlib import Path
from fastapi import HTTPException

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}


def find_image_files(target_dir: Path) -> tuple[list[Path], list[Path]]:
    """
    Recursively find all image and DICOM files in directory.
    Returns: (image_files, dicom_files) as lists of Path objects.
    """
    image_files = []
    dicom_files = []
    for dirpath, _, filenames in os.walk(target_dir):
        for f in filenames:
            ext = Path(f).suffix.lower()
            if ext in IMAGE_EXTENSIONS:
                image_files.append(Path(dirpath) / f)
            elif ext == '.dcm':
                dicom_files.append(Path(dirpath) / f)
    return image_files, dicom_files


def validate_zip_content_type(image_files: list[Path], dicom_files: list[Path]) -> str:
    """
    Validate ZIP contains only one type of content.
    Returns: 'dicom', 'images', 'mixed', or 'empty'
    """
    if dicom_files and image_files:
        return 'mixed'
    if dicom_files:
        return 'dicom'
    if image_files:
        return 'images'
    return 'empty'


def load_image_xray(file_path: Path) -> np.ndarray:
    """Load a single image file and return normalized grayscale array (256x256)."""
    img = cv2.imread(str(file_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {file_path}")
    # Resize to 256x256 to match XRayProcessor
    img_resized = cv2.resize(img, (256, 256))
    return img_resized.astype(np.float32) / 255.0


def classify_images_by_view(image_files: list[Path]) -> tuple[Path, Path]:
    """
    Use the ResNet classifier to determine which image is frontal/lateral.
    Returns: (frontal_path, lateral_path)
    """
    from .xray_classifier import classify_xray_view

    if len(image_files) != 2:
        raise HTTPException(
            status_code=400,
            detail=f"Expected exactly 2 images, found {len(image_files)}"
        )

    views = {}
    for img_path in image_files:
        arr = load_image_xray(img_path)
        view_type = classify_xray_view(arr)
        views[view_type] = img_path

    if 'frontal' not in views or 'lateral' not in views:
        raise HTTPException(
            status_code=400,
            detail="Could not classify images as frontal/lateral. Please ensure images are valid X-rays."
        )

    return views['frontal'], views['lateral']


def load_xrays_from_images(target_dir: Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Load and classify X-rays from image files (JPEG/PNG).
    Returns: (frontal_arr, lateral_arr) as normalized float32 arrays (256x256)
    """
    image_files, dicom_files = find_image_files(target_dir)

    if dicom_files:
        raise HTTPException(
            status_code=400,
            detail="ZIP contains DICOM files. For image-only input, remove DICOM files."
        )

    if not image_files:
        raise HTTPException(
            status_code=400,
            detail="No image files found in ZIP"
        )

    if len(image_files) != 2:
        raise HTTPException(
            status_code=400,
            detail=f"Expected exactly 2 images, found {len(image_files)}. Please provide exactly 2 X-ray images."
        )

    frontal_path, lateral_path = classify_images_by_view(image_files)

    frontal_arr = load_image_xray(frontal_path)
    lateral_arr = load_image_xray(lateral_path)

    return frontal_arr, lateral_arr
