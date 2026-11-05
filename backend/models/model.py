import os
import urllib.request
import pandas as pd
import numpy as np
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

DATA_URLS = [
    "https://raw.githubusercontent.com/Sadhana-Panthi/agricultural-crop-recommendation/main/Crop_recommendation.csv",
    "https://raw.githubusercontent.com/aakashr02/Crop-Recommendation/master/Crop_recommendation.csv",
    "https://raw.githubusercontent.com/animesh-agarwal/Machine-Learning/master/Crop_Recommendation/Crop_recommendation.csv"
]
DATA_PATH = "Crop_recommendation.csv"
MODEL_PATH = "crop_recommendation_model.pkl"
STATS_PATH = "crop_stats.json"

def download_data():
    if os.path.exists(DATA_PATH):
        print("Dataset already exists locally.")
        return
        
    for url in DATA_URLS:
        try:
            print(f"Trying to download dataset from: {url}...")
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                with open(DATA_PATH, 'wb') as out_file:
                    out_file.write(response.read())
            print("Download successful!")
            return
        except Exception as e:
            print(f"Failed to download from {url}. Error: {e}")
            
    raise Exception("Failed to download dataset from all sources.")



def train_and_analyze():
    # 1. Load Data
    df = pd.read_csv(DATA_PATH)
    print(f"Dataset shape: {df.shape}")
    
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    
    # 2. Compute statistics for Scenario 2 (Crop Suitability) and Scenario 3 (Analytics)
    # We will compute min, max, mean, std, and 10th/90th percentiles for each crop and feature
    crop_stats = {}
    crops = df['label'].unique()
    
    for crop in crops:
        crop_df = df[df['label'] == crop]
        crop_stats[crop] = {}
        for feature in features:
            values = crop_df[feature].values
            crop_stats[crop][feature] = {
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'p10': float(np.percentile(values, 10)),
                'p90': float(np.percentile(values, 90))
            }
            
    with open(STATS_PATH, 'w') as f:
        json.dump(crop_stats, f, indent=4)
    print(f"Saved crop statistics to {STATS_PATH}")
    
    # 3. Train Model
    X = df[features]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Training Accuracy: {accuracy * 100:.2f}%")
    
    # Save Model
    joblib.dump(model, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")

if __name__ == "__main__":
    download_data()
    train_and_analyze()
