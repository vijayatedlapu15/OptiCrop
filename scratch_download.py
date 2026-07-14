import os
import pandas as pd

url = "https://raw.githubusercontent.com/AayushPanchal-04/Crop-Recommendation-System/main/data/Crop_recommendation.csv"

print("Downloading dataset from URL...")
try:
    df = pd.read_csv(url)
    print("Dataset downloaded successfully!")
    print("Shape:", df.shape)
    print("Columns:", list(df.columns))
    print("Unique crops:", list(df['label'].unique()))
    print("Summary statistics:")
    print(df.describe())
    
    # Calculate crop-wise statistics for suitability assessment
    crop_stats = df.groupby('label').agg(['min', 'max', 'mean'])
    print("\nSample crop statistics for rice:")
    print(crop_stats.loc['rice'])
except Exception as e:
    print("Error:", e)
