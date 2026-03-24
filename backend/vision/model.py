"""
model.py
--------
PyTorch CNN model definitions using MobileNetV2 (torchvision).

  Stage 1 – AccidentDetector   : binary classification (sigmoid)
  Stage 2 – SeverityClassifier : 3-class softmax
"""

import torch
import torch.nn as nn
from torchvision import models
from torchvision.models import MobileNet_V2_Weights


# ─────────────────────────────────────────────────────────
# SHARED BASE
# ─────────────────────────────────────────────────────────

class _MobileNetBase(nn.Module):
    """Shared backbone (frozen MobileNetV2) + configurable classification head."""

    def __init__(self, num_classes: int, dropout: float = 0.3):
        super().__init__()

        backbone = models.mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)

        # Freeze backbone
        for param in backbone.parameters():
            param.requires_grad = False

        # Feature extractor (everything except the original classifier)
        self.features = backbone.features

        self.pool = nn.AdaptiveAvgPool2d(1)

        in_features = backbone.last_channel   # 1280 for MobileNetV2

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_features, 256),
            nn.BatchNorm1d(256),
            nn.GELU(),                # Advanced activation used in ViTs
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        x = self.classifier(x)
        return x

    def unfreeze_top(self, n_layers: int = 5):
        """Unfreeze the last `n_layers` of the MobileNetV2 features block."""
        feature_layers = list(self.features.children())
        for layer in feature_layers[-n_layers:]:
            for param in layer.parameters():
                param.requires_grad = True
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f"[Fine-tune] Top {n_layers} backbone layers unfrozen  |  "
              f"Trainable params: {trainable:,}")


# ─────────────────────────────────────────────────────────
# STAGE 1 – BINARY ACCIDENT DETECTOR
# ─────────────────────────────────────────────────────────

class AccidentDetector(_MobileNetBase):
    """
    Binary classifier: Accident vs. NonAccident.
    Output: raw logit (1 unit). Apply sigmoid for probability.
    Use BCEWithLogitsLoss during training.
    """

    def __init__(self, dropout: float = 0.3):
        super().__init__(num_classes=1, dropout=dropout)
        total = sum(p.numel() for p in self.parameters())
        train = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f"[Stage 1] AccidentDetector built  |  "
              f"Total params: {total:,}  |  Trainable: {train:,}")


# ─────────────────────────────────────────────────────────
# STAGE 2 – SEVERITY CLASSIFIER
# ─────────────────────────────────────────────────────────

class SeverityClassifier(_MobileNetBase):
    """
    3-class classifier: Severity Level 1 / 2 / 3.
    Output: raw logits (3 units). Apply softmax for probabilities.
    Use CrossEntropyLoss during training.
    """

    def __init__(self, num_classes: int = 3, dropout: float = 0.3):
        super().__init__(num_classes=num_classes, dropout=dropout)
        total = sum(p.numel() for p in self.parameters())
        train = sum(p.numel() for p in self.parameters() if p.requires_grad)
        print(f"[Stage 2] SeverityClassifier built  |  "
              f"Total params: {total:,}  |  Trainable: {train:,}")


# ─────────────────────────────────────────────────────────
# DEVICE HELPER
# ─────────────────────────────────────────────────────────

def get_device() -> torch.device:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Device] Using: {device}")
    return device


# ─────────────────────────────────────────────────────────
# QUICK SELF-TEST
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    device = get_device()
    dummy  = torch.randn(2, 3, 224, 224).to(device)

    m1 = AccidentDetector().to(device)
    out1 = m1(dummy)
    print(f"Stage 1 output shape: {out1.shape}   (expect [2, 1])")
    print(f"Stage 1 sigmoid probs: {torch.sigmoid(out1).squeeze().tolist()}")

    m2 = SeverityClassifier().to(device)
    out2 = m2(dummy)
    print(f"\nStage 2 output shape: {out2.shape}   (expect [2, 3])")
    print(f"Stage 2 softmax probs:\n{torch.softmax(out2, dim=1)}")