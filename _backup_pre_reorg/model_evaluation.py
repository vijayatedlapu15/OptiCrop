import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "Crop_recommendation.csv")
MODEL_PATH = os.path.join(BASE_DIR, "crop_recommendation_model.pkl")
OUTPUT_PATH = os.path.join(BASE_DIR, "evaluation_metrics.json")

def evaluate_random_forest():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}")
        
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    X = df[features]
    y = df['label']
    
    # 80/20 train/test split matching model.py exactly
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Loading trained Random Forest model from {MODEL_PATH}...")
    model = joblib.load(MODEL_PATH)
    
    print("Evaluating model on 440 unseen test samples...")
    y_pred = model.predict(X_test)
    
    # Genuine multiclass metrics
    acc = float(accuracy_score(y_test, y_pred))
    prec_macro = float(precision_score(y_test, y_pred, average='macro'))
    prec_weighted = float(precision_score(y_test, y_pred, average='weighted'))
    rec_macro = float(recall_score(y_test, y_pred, average='macro'))
    rec_weighted = float(recall_score(y_test, y_pred, average='weighted'))
    f1_mac = float(f1_score(y_test, y_pred, average='macro'))
    f1_weight = float(f1_score(y_test, y_pred, average='weighted'))
    
    # Class labels
    classes = sorted(list(df['label'].unique()))
    cm = confusion_matrix(y_test, y_pred, labels=classes).tolist()
    
    # Per-class classification report
    report = classification_report(y_test, y_pred, target_names=classes, output_dict=True)
    per_class_metrics = {}
    for c in classes:
        per_class_metrics[c.capitalize()] = {
            'precision': round(float(report[c]['precision']) * 100, 2),
            'recall': round(float(report[c]['recall']) * 100, 2),
            'f1_score': round(float(report[c]['f1-score']) * 100, 2),
            'support': int(report[c]['support'])
        }
        
    # Feature importances directly from Random Forest (MDI)
    importances = model.feature_importances_
    feature_importance_list = []
    feature_labels = {
        'N': 'Nitrogen (N)',
        'P': 'Phosphorus (P)',
        'K': 'Potassium (K)',
        'temperature': 'Temperature (°C)',
        'humidity': 'Humidity (%)',
        'ph': 'Soil pH',
        'rainfall': 'Rainfall (mm)'
    }
    for feat, imp in zip(features, importances):
        feature_importance_list.append({
            'feature': feat,
            'name': feature_labels[feat],
            'importance_percentage': round(float(imp) * 100, 2)
        })
    # Sort descending
    feature_importance_list.sort(key=lambda x: x['importance_percentage'], reverse=True)
    
    result = {
        'model_name': 'Random Forest Classifier',
        'n_estimators': 100,
        'dataset_total_samples': len(df),
        'test_samples_evaluated': len(X_test),
        'metrics': {
            'accuracy': round(acc * 100, 2),
            'precision_macro': round(prec_macro * 100, 2),
            'precision_weighted': round(prec_weighted * 100, 2),
            'recall_macro': round(rec_macro * 100, 2),
            'recall_weighted': round(rec_weighted * 100, 2),
            'f1_macro': round(f1_mac * 100, 2),
            'f1_weighted': round(f1_weight * 100, 2)
        },
        'feature_importance': feature_importance_list,
        'per_class_metrics': per_class_metrics,
        'confusion_matrix': cm,
        'classes': [c.capitalize() for c in classes]
    }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(result, f, indent=4)
        
    print(f"Evaluation metrics successfully saved to {OUTPUT_PATH}")
    print(f"Accuracy: {result['metrics']['accuracy']}%")
    print(f"Weighted F1: {result['metrics']['f1_weighted']}%")
    print(f"Macro F1: {result['metrics']['f1_macro']}%")
    return result

if __name__ == '__main__':
    evaluate_random_forest()
