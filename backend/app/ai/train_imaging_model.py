"""
Trains a small CNN to classify chest X-rays as Normal vs. Pneumonia.

IMPORTANT — read before treating this as production-ready:
This is trained on a 34-image balanced subset (17 normal / 17 pneumonia,
frontal + supine views) of the public ieee8023/covid-chestxray-dataset —
the largest real, freely-downloadable set this environment's network
access allowed. The "No Finding" (normal) class is a genuine hard limit
of this source dataset: it contains only 18 normal X-rays total across
~950 rows (it's a COVID/pneumonia case-report dataset, not a general
radiology archive), so 17 is close to the ceiling available here without
a larger dataset download this sandbox's network access doesn't permit
(pretrained ImageNet weight downloads and full Kaggle-mirror repo
downloads were both tried and blocked/impractical — see commit history).

Because N=34 makes any single train/test split extremely noisy (a 6-image
holdout can only land on 0%, 17%, 33%, 50%, 67%, 83%, or 100% — none of
which is a meaningful accuracy estimate), this script uses stratified
5-fold cross-validation and reports the mean +/- std across folds. That
number should be read as "the pipeline works end-to-end and does better
than chance on this tiny sample" evidence, not as a claim of diagnostic
performance.

For a real hackathon submission, retrain this on the full Kaggle
"Chest X-Ray Images (Pneumonia)" dataset (5,856 images) — swap the data
directory below and rerun; nothing else in the pipeline (API route,
Grad-CAM, frontend) needs to change.

Run: python -m app.ai.train_imaging_model
Produces: app/ai/models/imaging_model.pt
"""
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
from sklearn.model_selection import StratifiedKFold
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

DATA_DIR = Path(__file__).parent / "imaging_data" / "raw"
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

IMG_SIZE = 128
CLASSES = ["normal", "pneumonia"]
N_FOLDS = 5
N_EPOCHS = 25

torch.manual_seed(42)
random.seed(42)
np.random.seed(42)

TRAIN_TRANSFORM = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(12),
    transforms.ColorJitter(brightness=0.25, contrast=0.25),
    transforms.ToTensor(),
])
EVAL_TRANSFORM = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])


class ChestXrayDataset(Dataset):
    def __init__(self, samples: list[tuple[Path, int]], train: bool):
        self.samples = samples
        self.transform = TRAIN_TRANSFORM if train else EVAL_TRANSFORM

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        image = Image.open(path).convert("RGB")
        return self.transform(image), label


class SmallChestXrayCNN(nn.Module):
    """Deliberately small — this dataset is far too small to justify a deep network."""

    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.BatchNorm2d(16), nn.ReLU(), nn.MaxPool2d(2),   # 128 -> 64
            nn.Conv2d(16, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),  # 64 -> 32
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),  # 32 -> 16
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(4),
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(64 * 4 * 4, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 2),
        )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


def _load_samples() -> list[tuple[Path, int]]:
    samples = []
    for label, cls in enumerate(CLASSES):
        for path in sorted((DATA_DIR / cls).glob("*")):
            samples.append((path, label))
    return samples


def _train_one_model(train_samples: list, n_epochs: int) -> SmallChestXrayCNN:
    loader = DataLoader(ChestXrayDataset(train_samples, train=True), batch_size=8, shuffle=True)
    model = SmallChestXrayCNN()
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-3)
    criterion = nn.CrossEntropyLoss()

    model.train()
    for _ in range(n_epochs):
        for images, labels in loader:
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
    return model


def _evaluate(model: SmallChestXrayCNN, samples: list) -> float:
    loader = DataLoader(ChestXrayDataset(samples, train=False), batch_size=8)
    model.eval()
    correct = 0
    with torch.no_grad():
        for images, labels in loader:
            preds = model(images).argmax(dim=1)
            correct += (preds == labels).sum().item()
    return correct / len(samples) if samples else 0.0


def train() -> None:
    samples = _load_samples()
    labels = np.array([label for _, label in samples])
    print(f"Total images: {len(samples)} ({(labels == 0).sum()} normal, {(labels == 1).sum()} pneumonia)")

    # Stratified k-fold cross-validation for an honest accuracy estimate on tiny N.
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
    fold_accuracies = []
    for fold_idx, (train_idx, val_idx) in enumerate(skf.split(samples, labels)):
        train_samples = [samples[i] for i in train_idx]
        val_samples = [samples[i] for i in val_idx]
        model = _train_one_model(train_samples, N_EPOCHS)
        acc = _evaluate(model, val_samples)
        fold_accuracies.append(acc)
        print(f"Fold {fold_idx + 1}/{N_FOLDS}: {acc:.3f} ({len(val_samples)} val images)")

    mean_acc = float(np.mean(fold_accuracies))
    std_acc = float(np.std(fold_accuracies))
    print(f"\nCross-validated accuracy: {mean_acc:.3f} +/- {std_acc:.3f} across {N_FOLDS} folds")

    # Final model trained on ALL available data (standard practice once CV has
    # validated the pipeline) — this is the model the API actually serves.
    final_model = _train_one_model(samples, N_EPOCHS)
    torch.save(
        {
            "model_state": final_model.state_dict(),
            "cv_mean_accuracy": round(mean_acc, 3),
            "cv_std_accuracy": round(std_acc, 3),
            "n_folds": N_FOLDS,
            "n_total": len(samples),
        },
        MODELS_DIR / "imaging_model.pt",
    )
    print(f"Saved final model (trained on all {len(samples)} images) -> {MODELS_DIR / 'imaging_model.pt'}")


if __name__ == "__main__":
    train()
