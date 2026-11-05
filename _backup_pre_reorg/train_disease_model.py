"""
MobileNetV2 Plant Disease Training Pipeline for OptiCrop.
Dataset: PlantVillage (38 classes, ~54K images)
Source: https://github.com/spMohanty/PlantVillage-Dataset (CC0 1.0)
Architecture: MobileNetV2 transfer learning from ImageNet
"""
import os
import sys
import json
import time
import random
import numpy as np
from PIL import Image

# ---- Configuration ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "datasets", "plantvillage")
OUTPUT_DIR = os.path.join(BASE_DIR, "training_output")
CHECKPOINT_PATH = os.path.join(OUTPUT_DIR, "best_model.pth")
CLASS_MAP_PATH = os.path.join(OUTPUT_DIR, "class_mapping.json")
TRAIN_LOG_PATH = os.path.join(OUTPUT_DIR, "training_log.json")
EVAL_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "disease_evaluation.json")

# Hyperparameters
BATCH_SIZE = 32
NUM_EPOCHS = 5
LEARNING_RATE = 0.001
SEED = 42
VAL_SPLIT = 0.15
TEST_SPLIT = 0.10
IMG_SIZE = 224
NUM_WORKERS = 0  # Windows compatibility

def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass

def verify_dataset():
    """Verify dataset exists and count classes/images."""
    if not os.path.exists(DATASET_DIR):
        print(f"ERROR: Dataset not found at {DATASET_DIR}")
        print("Run: python download_plantvillage.py")
        return None
    
    classes = sorted([d for d in os.listdir(DATASET_DIR) 
                      if os.path.isdir(os.path.join(DATASET_DIR, d))])
    
    if len(classes) < 2:
        print(f"ERROR: Only {len(classes)} class directories found")
        return None
    
    class_counts = {}
    total = 0
    for cls in classes:
        cls_dir = os.path.join(DATASET_DIR, cls)
        imgs = [f for f in os.listdir(cls_dir) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'))]
        class_counts[cls] = len(imgs)
        total += len(imgs)
    
    print(f"Dataset verified: {len(classes)} classes, {total} total images")
    return {'classes': classes, 'counts': class_counts, 'total': total}

def create_splits(dataset_info):
    """Create stratified train/val/test splits. Returns file paths per split."""
    set_seed()
    classes = dataset_info['classes']
    
    train_files, val_files, test_files = [], [], []
    
    for cls_idx, cls_name in enumerate(classes):
        cls_dir = os.path.join(DATASET_DIR, cls_name)
        imgs = sorted([f for f in os.listdir(cls_dir) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'))])
        random.shuffle(imgs)
        
        n = len(imgs)
        n_test = max(1, int(n * TEST_SPLIT))
        n_val = max(1, int(n * VAL_SPLIT))
        n_train = n - n_test - n_val
        
        for img in imgs[:n_train]:
            train_files.append((os.path.join(cls_dir, img), cls_idx))
        for img in imgs[n_train:n_train + n_val]:
            val_files.append((os.path.join(cls_dir, img), cls_idx))
        for img in imgs[n_train + n_val:]:
            test_files.append((os.path.join(cls_dir, img), cls_idx))
    
    random.shuffle(train_files)
    
    print(f"Split: train={len(train_files)}, val={len(val_files)}, test={len(test_files)}")
    return train_files, val_files, test_files

def train_model():
    """Full training pipeline."""
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torchvision import models, transforms
    from torch.utils.data import Dataset, DataLoader
    
    set_seed()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Verify dataset
    dataset_info = verify_dataset()
    if dataset_info is None:
        return False
    
    classes = dataset_info['classes']
    num_classes = len(classes)
    
    # Save class mapping
    class_mapping = {i: name for i, name in enumerate(classes)}
    with open(CLASS_MAP_PATH, 'w') as f:
        json.dump(class_mapping, f, indent=2)
    print(f"Saved class mapping ({num_classes} classes) to {CLASS_MAP_PATH}")
    
    # 2. Create splits
    train_files, val_files, test_files = create_splits(dataset_info)
    
    # 3. Transforms
    train_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    val_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # 4. Dataset class
    class PlantDataset(Dataset):
        def __init__(self, file_list, transform=None):
            self.file_list = file_list
            self.transform = transform
        
        def __len__(self):
            return len(self.file_list)
        
        def __getitem__(self, idx):
            path, label = self.file_list[idx]
            try:
                img = Image.open(path).convert('RGB')
            except Exception:
                # Return a black image if file is corrupt
                img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), (0, 0, 0))
            if self.transform:
                img = self.transform(img)
            return img, label
    
    train_dataset = PlantDataset(train_files, train_transform)
    val_dataset = PlantDataset(val_files, val_transform)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)
    
    # 5. Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    # Freeze early layers, fine-tune later layers
    for param in model.features[:14].parameters():
        param.requires_grad = False
    
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes)
    )
    model = model.to(device)
    
    # 6. Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=4, gamma=0.1)
    
    # 7. Training loop
    best_val_acc = 0.0
    training_log = []
    
    print(f"\nStarting training: {NUM_EPOCHS} epochs, {len(train_loader)} batches/epoch")
    print("=" * 60)
    
    for epoch in range(NUM_EPOCHS):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        epoch_start = time.time()
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            if (batch_idx + 1) % 50 == 0:
                print(f"  Epoch {epoch+1}/{NUM_EPOCHS} | Batch {batch_idx+1}/{len(train_loader)} | "
                      f"Loss: {running_loss/(batch_idx+1):.4f} | Acc: {100.*correct/total:.2f}%")
        
        train_acc = 100. * correct / total
        train_loss = running_loss / len(train_loader)
        
        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        val_loss = 0.0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        
        val_acc = 100. * val_correct / val_total
        val_loss = val_loss / len(val_loader)
        epoch_time = time.time() - epoch_start
        
        scheduler.step()
        
        epoch_log = {
            'epoch': epoch + 1,
            'train_loss': round(train_loss, 4),
            'train_acc': round(train_acc, 2),
            'val_loss': round(val_loss, 4),
            'val_acc': round(val_acc, 2),
            'time_seconds': round(epoch_time, 1),
            'lr': optimizer.param_groups[0]['lr']
        }
        training_log.append(epoch_log)
        
        print(f"Epoch {epoch+1}/{NUM_EPOCHS} complete | "
              f"Train: {train_acc:.2f}% | Val: {val_acc:.2f}% | "
              f"Time: {epoch_time:.1f}s")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'num_classes': num_classes,
                'class_mapping': class_mapping
            }, CHECKPOINT_PATH)
            print(f"  -> New best model saved (val_acc={val_acc:.2f}%)")
        
        # Save training log after each epoch (resumability)
        with open(TRAIN_LOG_PATH, 'w') as f:
            json.dump({'epochs': training_log, 'best_val_acc': best_val_acc}, f, indent=2)
    
    print(f"\nTraining complete. Best validation accuracy: {best_val_acc:.2f}%")
    print(f"Best model saved to: {CHECKPOINT_PATH}")
    return True

def evaluate_model():
    """Evaluate on held-out test set."""
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    from torch.utils.data import Dataset, DataLoader
    from collections import defaultdict
    
    set_seed()
    
    if not os.path.exists(CHECKPOINT_PATH):
        print(f"ERROR: No trained model at {CHECKPOINT_PATH}")
        return False
    
    if not os.path.exists(CLASS_MAP_PATH):
        print(f"ERROR: No class mapping at {CLASS_MAP_PATH}")
        return False
    
    # Load class mapping
    with open(CLASS_MAP_PATH) as f:
        class_mapping = json.load(f)
    num_classes = len(class_mapping)
    classes = [class_mapping[str(i)] for i in range(num_classes)]
    
    # Verify dataset and get test split
    dataset_info = verify_dataset()
    if dataset_info is None:
        return False
    
    _, _, test_files = create_splits(dataset_info)
    
    # Transform
    transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    class SimpleDataset(Dataset):
        def __init__(self, file_list, transform):
            self.file_list = file_list
            self.transform = transform
        def __len__(self):
            return len(self.file_list)
        def __getitem__(self, idx):
            path, label = self.file_list[idx]
            try:
                img = Image.open(path).convert('RGB')
            except Exception:
                img = Image.new('RGB', (IMG_SIZE, IMG_SIZE))
            return self.transform(img), label
    
    test_dataset = SimpleDataset(test_files, transform)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)
    
    # Load model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = models.mobilenet_v2(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes)
    )
    
    checkpoint = torch.load(CHECKPOINT_PATH, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    # Evaluate
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            _, predicted = outputs.max(1)
            all_preds.extend(predicted.cpu().numpy().tolist())
            all_labels.extend(labels.numpy().tolist())
    
    # Metrics
    from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                                  f1_score, classification_report, confusion_matrix)
    
    acc = accuracy_score(all_labels, all_preds)
    prec_macro = precision_score(all_labels, all_preds, average='macro', zero_division=0)
    rec_macro = recall_score(all_labels, all_preds, average='macro', zero_division=0)
    f1_mac = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    f1_wt = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    report = classification_report(all_labels, all_preds, target_names=classes, 
                                    output_dict=True, zero_division=0)
    cm = confusion_matrix(all_labels, all_preds).tolist()
    
    per_class = {}
    for i, cls in enumerate(classes):
        per_class[cls] = {
            'precision': round(report[cls]['precision'] * 100, 2),
            'recall': round(report[cls]['recall'] * 100, 2),
            'f1_score': round(report[cls]['f1-score'] * 100, 2),
            'support': report[cls]['support']
        }
    
    result = {
        'model': 'MobileNetV2 (transfer learning)',
        'dataset': 'PlantVillage',
        'test_samples': len(all_labels),
        'num_classes': num_classes,
        'metrics': {
            'accuracy': round(acc * 100, 2),
            'precision_macro': round(prec_macro * 100, 2),
            'recall_macro': round(rec_macro * 100, 2),
            'f1_macro': round(f1_mac * 100, 2),
            'f1_weighted': round(f1_wt * 100, 2)
        },
        'per_class_metrics': per_class,
        'confusion_matrix': cm,
        'classes': classes
    }
    
    with open(EVAL_OUTPUT_PATH, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nTest Evaluation Results:")
    print(f"  Accuracy:      {result['metrics']['accuracy']}%")
    print(f"  F1 (macro):    {result['metrics']['f1_macro']}%")
    print(f"  F1 (weighted): {result['metrics']['f1_weighted']}%")
    print(f"  Test samples:  {result['test_samples']}")
    print(f"Saved to: {EVAL_OUTPUT_PATH}")
    return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'evaluate':
        evaluate_model()
    else:
        if train_model():
            evaluate_model()
