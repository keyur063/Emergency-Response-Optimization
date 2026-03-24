import os
import sys
import argparse
import torch
from PIL import Image
from torchvision import transforms

from vision.model import AccidentDetector, SeverityClassifier, get_device

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(os.path.dirname(BASE_DIR), "artifacts")
STAGE1_PATH = os.path.join(MODEL_DIR, "stage1_accident_detector.pth")
STAGE2_PATH = os.path.join(MODEL_DIR, "stage2_severity_classifier.pth")

IMG_SIZE = 224
AMBULANCE_SEVERITY_IDX = 1

TRANSFORM = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

_cache = {}

def _load_models(device):
    if "stage1" not in _cache:
        if not os.path.exists(STAGE1_PATH):
            sys.exit(f"[ERROR] Stage 1 model not found: {STAGE1_PATH}")
        m1 = AccidentDetector().to(device)
        m1.load_state_dict(torch.load(STAGE1_PATH, map_location=device))
        m1.eval()
        _cache["stage1"] = m1

    if "stage2" not in _cache:
        if not os.path.exists(STAGE2_PATH):
            sys.exit(f"[ERROR] Stage 2 model not found: {STAGE2_PATH}")
        m2 = SeverityClassifier(num_classes=3).to(device)
        m2.load_state_dict(torch.load(STAGE2_PATH, map_location=device))
        m2.eval()
        _cache["stage2"] = m2

    return _cache["stage1"], _cache["stage2"]

def predict(image_input, accident_threshold: float = 0.5, verbose: bool = True) -> dict:
    device = get_device()
    stage1, stage2 = _load_models(device)

    # Apply Transform BEFORE unsqueezing to prevent errors
    # Accept raw image from FastAPI OR a file path string
    if isinstance(image_input, str):
        img = Image.open(image_input).convert("RGB")
    else:
        img = image_input.convert("RGB")

    tensor = TRANSFORM(img).unsqueeze(0).to(device)  # type: ignore

    with torch.no_grad():
        logit1 = stage1(tensor).squeeze(dim=0) if tensor.shape[0] == 1 else stage1(tensor).squeeze()
        acc_prob = torch.sigmoid(logit1).item()

    is_accident = acc_prob >= accident_threshold

    result = {
        "is_accident": is_accident,
        "accident_conf": acc_prob,
        "severity_index": None,
        "severity_conf": None,
        "dispatch_ambulance": False,
    }

    if is_accident:
        with torch.no_grad():
            logits2 = stage2(tensor).squeeze(dim=0) if tensor.shape[0] == 1 else stage2(tensor).squeeze()
            probs2 = torch.softmax(logits2, dim=0)

        sev_idx = int(probs2.argmax().item())
        sev_conf = float(probs2[sev_idx].item())

        result["severity_index"] = sev_idx
        result["severity_conf"] = sev_conf
        result["dispatch_ambulance"] = (sev_idx >= AMBULANCE_SEVERITY_IDX)

    return result