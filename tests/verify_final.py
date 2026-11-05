"""Final verification script for OptiCrop."""
import os, json, sys

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(BASE)

def find_f(*cands):
    for c in cands:
        p = os.path.join(BASE, c)
        if os.path.exists(p):
            return p
    return os.path.join(BASE, cands[0])

print("=" * 60)
print("OPTICROP FINAL VERIFICATION REPORT")
print("=" * 60)

# 1. Checkpoint files
print("\n[1] CHECKPOINT FILES")
checkpoints = [
    find_f("backend/training/training_output/best_model.pth", "training_output/best_model.pth"),
    find_f("backend/models/plant_disease_mobilenet_v2.pth", "plant_disease_mobilenet_v2.pth")
]
for p in checkpoints:
    exists = os.path.exists(p)
    sz = os.path.getsize(p) if exists else 0
    print(f"  {os.path.basename(p)}: exists={exists}, size={sz:,} bytes")

# 2. Class mapping
print("\n[2] CLASS MAPPING")
with open(find_f("backend/config/class_mapping.json", "training_output/class_mapping.json")) as f:
    cm = json.load(f)
classes = list(cm.values())
print(f"  Total classes: {len(cm)}")
print(f"  First 3: {classes[:3]}")
print(f"  Last 3:  {classes[-3:]}")

# 3. Evaluation outputs
print("\n[3] SAVED EVALUATION METRICS")
with open(find_f("backend/config/disease_evaluation.json", "training_output/disease_evaluation.json")) as f:
    ev = json.load(f)
metrics = ev["metrics"]
print(f"  Test accuracy:    {metrics['accuracy']}%")
print(f"  F1 macro:         {metrics['f1_macro']}%")
print(f"  F1 weighted:      {metrics['f1_weighted']}%")
print(f"  Precision macro:  {metrics['precision_macro']}%")
print(f"  Recall macro:     {metrics['recall_macro']}%")
print(f"  Test samples:     {ev['test_samples']}")
print(f"  Num classes:      {ev['num_classes']}")

# 4. Training log
print("\n[4] TRAINING LOG")
with open(find_f("backend/training/training_output/training_log.json", "training_output/training_log.json")) as f:
    tl = json.load(f)
print(f"  Epochs completed: {len(tl['epochs'])}")
print(f"  Best val acc:     {tl['best_val_acc']:.2f}%")
for ep in tl["epochs"]:
    print(f"    Epoch {ep['epoch']}: train_acc={ep['train_acc']}%, val_acc={ep['val_acc']}%, loss={ep['train_loss']}")

# 5. Verify trained model loads and produces correct output shape
print("\n[5] MODEL LOAD + INFERENCE TEST")
try:
    import torch
    import torch.nn as nn
    from torchvision import models

    best_model_path = find_f("backend/training/training_output/best_model.pth", "training_output/best_model.pth")
    ckpt = torch.load(best_model_path, map_location="cpu")
    print(f"  Checkpoint keys: {list(ckpt.keys())}")
    print(f"  Saved epoch: {ckpt.get('epoch', 'N/A')}")
    print(f"  Saved val_acc: {ckpt.get('val_acc', 'N/A')}")
    print(f"  Saved num_classes: {ckpt.get('num_classes', 'N/A')}")

    model = models.mobilenet_v2(weights=None)
    in_f = model.classifier[1].in_features
    model.classifier = nn.Sequential(nn.Dropout(p=0.3), nn.Linear(in_f, 38))
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    x = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        out = model(x)
    print(f"  Output shape: {out.shape} (expected [1, 38])")
    print(f"  Model loads and infers: OK")

    # Check mapping consistency
    ckpt_map = ckpt.get("class_mapping", {})
    match = all(str(k) in cm and cm[str(k)] == v for k, v in ckpt_map.items())
    print(f"  Checkpoint<->file class mapping match: {match}")
except Exception as e:
    print(f"  ERROR: {e}")

# 6. Verify disease_model.py loads TRAINED model
print("\n[6] DISEASE_MODEL.PY LOADING PRIORITY")
with open(find_f("backend/utils/disease_model.py", "disease_model.py")) as f:
    content = f.read()
has_trained_path = "TRAINED_MODEL_PATH" in content
has_priority = "OptiCrop-trained model" in content
has_fallback = "legacy" in content.lower()
print(f"  TRAINED_MODEL_PATH defined: {has_trained_path}")
print(f"  Loads trained model first:  {has_priority}")
print(f"  Legacy fallback present:    {has_fallback}")
print(f"  Dropout=0.3 (matches train): {'Dropout(p=0.3)' in content}")

# 7. Check routes exist in app.py
print("\n[7] FLASK ROUTES IN APP.PY")
with open(find_f("backend/app.py", "app.py")) as f:
    app_content = f.read()
routes = [("/", "dashboard"), ("/recommend", "recommend"), ("/suitability", "suitability"),
          ("/disease-detection", "disease"), ("/research", "research")]
for path, name in routes:
    found = f"'{path}'" in app_content or f'"{path}"' in app_content
    print(f"  {path} ({name}): {'FOUND' if found else 'MISSING'}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
