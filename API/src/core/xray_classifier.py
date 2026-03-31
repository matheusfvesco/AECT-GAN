"""X-Ray view classifier using a trained ResNet18 model."""

from typing import Union
from pathlib import Path

import numpy as np
import torch
from torchvision import transforms
from PIL import Image
import timm


MODEL_NAME = "resnet18"
NUM_CLASSES = 2
IMAGE_SIZE = 224

# ImageNet normalization values
NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD = [0.229, 0.224, 0.225]

_TRANSFORMS = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD),
])


def _preprocess_array(xray_arr: np.ndarray) -> torch.Tensor:
    """Preprocess a 2D xray array for classification."""
    if xray_arr.ndim != 2:
        raise ValueError(f"Expected 2D array, got shape {xray_arr.shape}")

    # Normalize to 0-255 if needed and convert to uint8
    if xray_arr.max() <= 1.0:
        xray_arr = (xray_arr * 255).astype(np.uint8)
    elif xray_arr.max() <= 255:
        xray_arr = xray_arr.astype(np.uint8)
    else:
        xray_arr = np.clip(xray_arr, 0, 255).astype(np.uint8)

    # Convert to PIL Image and then to RGB
    pil_image = Image.fromarray(xray_arr, mode="L")
    rgb_image = pil_image.convert("RGB")

    # Apply transforms and add batch dimension
    tensor = _TRANSFORMS(rgb_image)
    return tensor.unsqueeze(0)


def classify_xray_view(
    xray_arr: np.ndarray,
    weights_path: Union[Path, str, None] = None,
) -> str:
    """
    Classify an x-ray array as 'frontal' or 'lateral'.

    Model is loaded and deleted per call to minimize GPU memory usage.

    Args:
        xray_arr: 2D numpy array of shape (H, W).
        weights_path: Optional path to model weights. Defaults to API/weights/xray_classifier.pth.

    Returns:
        'frontal' or 'lateral'.
    """
    if weights_path is None:
        weights_path = Path("API/weights/xray_classifier.pth")
    weights_path = Path(weights_path)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # Load model fresh for each inference
    model = timm.create_model(MODEL_NAME, pretrained=False, num_classes=NUM_CLASSES)
    state_dict = torch.load(weights_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    # Preprocess and infer
    tensor = _preprocess_array(xray_arr).to(device)

    with torch.no_grad():
        logits = model(tensor)
        predicted_class = torch.argmax(logits, dim=1).item()

    # Cleanup: delete model and sync CUDA
    del model
    if torch.cuda.is_available():
        torch.cuda.synchronize()

    return "lateral" if predicted_class == 1 else "frontal"