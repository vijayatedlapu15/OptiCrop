"""Convert the OptiCrop-trained MobileNetV2 model to ONNX format for Vercel deployment."""
import torch
import torch.nn as nn
from torchvision import models
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINED_PATH = os.path.join(BASE_DIR, 'training_output', 'best_model.pth')
LEGACY_PATH = os.path.join(BASE_DIR, 'plant_disease_mobilenet_v2.pth')
ONNX_PATH = os.path.join(BASE_DIR, 'plant_disease_model.onnx')
CLASS_MAP_OUT = os.path.join(BASE_DIR, 'class_mapping.json')

NUM_CLASSES = 38

# Build model architecture (must match training: Dropout 0.3)
model = models.mobilenet_v2(weights=None)
in_features = model.classifier[1].in_features
model.classifier = nn.Sequential(
    nn.Dropout(p=0.3),
    nn.Linear(in_features, NUM_CLASSES)
)

# Load the trained model first, fallback to legacy
class_mapping = None
if os.path.exists(TRAINED_PATH):
    print(f"Loading trained model: {TRAINED_PATH}")
    checkpoint = torch.load(TRAINED_PATH, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    class_mapping = checkpoint.get('class_mapping')
    print(f"  Epoch: {checkpoint.get('epoch')}, Val acc: {checkpoint.get('val_acc', 0):.2f}%")
elif os.path.exists(LEGACY_PATH):
    print(f"Loading legacy model: {LEGACY_PATH}")
    state_dict = torch.load(LEGACY_PATH, map_location='cpu')
    remap = {}
    for k, v in state_dict.items():
        new_k = k
        if k == 'classifier.1.1.weight':
            new_k = 'classifier.1.weight'
        elif k == 'classifier.1.1.bias':
            new_k = 'classifier.1.bias'
        remap[new_k] = v
    model.load_state_dict(remap, strict=False)
else:
    print("ERROR: No model weights found!")
    exit(1)

model.eval()

# Save class mapping alongside ONNX model
if class_mapping:
    with open(CLASS_MAP_OUT, 'w') as f:
        json.dump(class_mapping, f, indent=2)
    print(f"Class mapping saved: {CLASS_MAP_OUT} ({len(class_mapping)} classes)")

# Export to ONNX
dummy_input = torch.randn(1, 3, 224, 224)
print("Exporting to ONNX...")
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

# Consolidate external data into a standalone ONNX file if needed
try:
    import onnx
    m = onnx.load(ONNX_PATH, load_external_data=True)
    onnx.save_model(m, ONNX_PATH, save_as_external_data=False)
    data_path = ONNX_PATH + ".data"
    if os.path.exists(data_path):
        os.remove(data_path)
    print("Consolidated into self-contained standalone ONNX file.")
except Exception as e:
    print(f"Standalone consolidation notice: {e}")

onnx_size = os.path.getsize(ONNX_PATH)
print(f"\nONNX model saved: {ONNX_PATH}")
print(f"ONNX size: {onnx_size / 1024 / 1024:.1f} MB")
print("Done!")
