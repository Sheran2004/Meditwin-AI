"""
Inference + Grad-CAM for the chest X-ray classifier.

IMPORTANT: read app/ai/train_imaging_model.py's module docstring first.
The shipped model was trained on only 34 images (the ceiling of real,
downloadable "No Finding" chest X-rays this sandbox's restricted network
access allowed — pretrained ImageNet weights, GitHub API listing, and
several candidate dataset mirrors were all tried and either blocked or
unavailable) and evaluates at ~44% mean accuracy under 5-fold
cross-validation — i.e. no better than chance. This module is fully
functional (real preprocessing, real forward pass, real Grad-CAM) but its
*predictions* are not currently meaningful. Every response from
predict_pneumonia() carries an explicit `clinically_meaningful: False`
flag for exactly this reason — never remove that flag without retraining
on a proper-sized dataset (see the training script for how) and
re-validating accuracy on a held-out test set.
"""
import io
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from app.ai.train_imaging_model import IMG_SIZE, SmallChestXrayCNN

MODEL_PATH = Path(__file__).parent / "models" / "imaging_model.pt"

# Accuracy below which we refuse to present the number as meaningful at all —
# currently always true for the shipped 34-image model (see docstring above).
MEANINGFUL_ACCURACY_THRESHOLD = 0.80

_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])

_checkpoint = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
_model = SmallChestXrayCNN()
_model.load_state_dict(_checkpoint["model_state"])
_model.eval()
_CV_MEAN_ACCURACY = _checkpoint["cv_mean_accuracy"]
_CV_STD_ACCURACY = _checkpoint["cv_std_accuracy"]
_N_TOTAL = _checkpoint["n_total"]


def _grad_cam(image_tensor: torch.Tensor, target_class: int) -> np.ndarray:
    """Returns a (H, W) heatmap in [0, 1] highlighting regions that drove the prediction."""
    activations = {}
    gradients = {}

    last_conv = _model.features[-3]  # the Conv2d before the final ReLU+MaxPool
    def fwd_hook(_module, _input, output):
        activations["value"] = output
    def bwd_hook(_module, _grad_input, grad_output):
        gradients["value"] = grad_output[0]

    h1 = last_conv.register_forward_hook(fwd_hook)
    h2 = last_conv.register_full_backward_hook(bwd_hook)

    try:
        _model.zero_grad()
        output = _model(image_tensor.unsqueeze(0))
        output[0, target_class].backward()

        acts = activations["value"][0]      # (C, H, W)
        grads = gradients["value"][0]        # (C, H, W)
        weights = grads.mean(dim=(1, 2))     # (C,) — global average pooled gradient per channel

        cam = torch.relu((weights[:, None, None] * acts).sum(dim=0))
        cam = cam / (cam.max() + 1e-8)
        return cam.detach().numpy()
    finally:
        h1.remove()
        h2.remove()


def predict_pneumonia(image_bytes: bytes) -> dict:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = _transform(image)

    with torch.no_grad():
        logits = _model(tensor.unsqueeze(0))
        probs = F.softmax(logits, dim=1)[0]

    pred_class = int(probs.argmax())
    confidence_pct = round(float(probs[pred_class]) * 100, 1)
    cam = _grad_cam(tensor, pred_class)

    return {
        "prediction": "pneumonia" if pred_class == 1 else "normal",
        "confidence_pct": confidence_pct,
        "heatmap": cam.tolist(),  # small (16x16) grid; frontend upsamples/overlays it
        "clinically_meaningful": _CV_MEAN_ACCURACY >= MEANINGFUL_ACCURACY_THRESHOLD,
        "model_trained_on_n_images": _N_TOTAL,
        "model_cv_accuracy": round(_CV_MEAN_ACCURACY, 3),
        "model_cv_accuracy_std": round(_CV_STD_ACCURACY, 3),
        "warning": (
            None if _CV_MEAN_ACCURACY >= MEANINGFUL_ACCURACY_THRESHOLD else
            f"This model was trained on only {_N_TOTAL} images and is NOT clinically meaningful "
            f"(5-fold cross-validated accuracy is {_CV_MEAN_ACCURACY*100:.0f}% ± {_CV_STD_ACCURACY*100:.0f}%, "
            "at or below random chance). This response demonstrates the pipeline only — retrain on "
            "a proper-sized dataset (see app/ai/train_imaging_model.py) before presenting any "
            "prediction as real."
        ),
    }
