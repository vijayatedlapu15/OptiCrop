"""Convert PyTorch MobileNetV2 model to ONNX format for lightweight deployment."""
import torch
import torch.nn as nn
from torchvision import models
import os

# Number of PlantVillage classes
NUM_CLASSES = 38
WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), 'plant_disease_mobilenet_v2.pth')
ONNX_PATH = os.path.join(os.path.dirname(__file__), 'plant_disease_model.onnx')

# Build model architecture
model = models.mobilenet_v2(weights=None)
in_features = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Dropout(p=0.2),
    nn.Linear(in_features, NUM_CLASSES)
)

# Load weights
state_dict = torch.load(WEIGHTS_PATH, map_location='cpu')
# Remap keys if needed
remap = {}
for k, v in state_dict.items():
    new_k = k
    if k == 'classifier.1.1.weight':
        new_k = 'classifier.1.weight'
    elif k == 'classifier.1.1.bias':
        new_k = 'classifier.1.bias'
    remap[new_k] = v

model.load_state_dict(remap, strict=False)
model.eval()

# Create dummy input
dummy_input = torch.randn(1, 3, 224, 224)

# Export to ONNX
print("Exporting model to ONNX format...")
torch.onnx.export(
    model,
    dummy_input,
    ONNX_PATH,
    export_params=True,
    opset_version=11,
    do_constant_folding=True,
    input_names=['input'],
    output_names=['output'],
    dynamic_axes={
        'input': {0: 'batch_size'},
        'output': {0: 'batch_size'}
    }
)

onnx_size = os.path.getsize(ONNX_PATH)
pth_size = os.path.getsize(WEIGHTS_PATH)
print(f"ONNX model saved to: {ONNX_PATH}")
print(f"PyTorch model size: {pth_size / 1024 / 1024:.1f} MB")
print(f"ONNX model size: {onnx_size / 1024 / 1024:.1f} MB")
print(f"Size reduction: {(1 - onnx_size / pth_size) * 100:.1f}%")
print("Done!")
