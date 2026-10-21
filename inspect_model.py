"""Inspect the saved .pth model to determine if it was actually fine-tuned on PlantVillage or just saved from pretrained ImageNet weights."""
import torch
from torchvision import models
import torch.nn as nn

# Load saved weights
sd_saved = torch.load('plant_disease_mobilenet_v2.pth', map_location='cpu')

# Load fresh ImageNet-pretrained MobileNetV2
pretrained_model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
pretrained_sd = pretrained_model.state_dict()

# Compare feature extractor weights (backbone, NOT classifier)
same_count = 0
diff_count = 0
for k in pretrained_sd:
    if 'classifier' in k:
        continue  # Skip classifier — it was replaced
    if k in sd_saved:
        if torch.equal(pretrained_sd[k], sd_saved[k]):
            same_count += 1
        else:
            diff_count += 1
            print(f"  DIFFERENT: {k}")
    else:
        print(f"  MISSING from saved: {k}")

print(f"\nFeature backbone keys identical to ImageNet pretrained: {same_count}")
print(f"Feature backbone keys different from ImageNet pretrained: {diff_count}")

# Check classifier layer
print(f"\nClassifier output shape: {sd_saved['classifier.1.weight'].shape}")
print(f"This means the classifier was set up for {sd_saved['classifier.1.weight'].shape[0]} classes")

# Check if classifier weights look like random init or trained
cls_w = sd_saved['classifier.1.weight']
print(f"\nClassifier weight stats:")
print(f"  Mean: {cls_w.mean().item():.6f}")
print(f"  Std:  {cls_w.std().item():.6f}")
print(f"  Min:  {cls_w.min().item():.6f}")
print(f"  Max:  {cls_w.max().item():.6f}")

# Compare to what a fresh random Linear(1280, 38) looks like
fresh_linear = nn.Linear(1280, 38)
print(f"\nFresh random Linear(1280,38) weight stats for comparison:")
print(f"  Mean: {fresh_linear.weight.data.mean().item():.6f}")
print(f"  Std:  {fresh_linear.weight.data.std().item():.6f}")
