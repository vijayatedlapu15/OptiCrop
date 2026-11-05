"""
Alternative PlantVillage dataset downloader.
Downloads the color images only (~87MB) from a more reliable mirror.
Falls back to multiple sources if one fails.
"""
import os
import sys
import zipfile
import urllib.request
import ssl
import time

TRAINING_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(TRAINING_DIR)
DATASET_DIR = os.path.join(BACKEND_DIR, "datasets")
EXTRACT_DIR = os.path.join(DATASET_DIR, "plantvillage")

# Multiple mirrors to try (color images only - much smaller)
SOURCES = [
    {
        "name": "GitHub Color Only",
        "url": "https://github.com/spMohanty/PlantVillage-Dataset/raw/master/raw/color/Apple___Apple_scab/0a5e9801-2443-4476-8dde-8d9e75210e26___FREC_Scab%203335.JPG",
        "type": "individual"  # Will use git sparse checkout
    }
]

# We'll use a different approach - download via the GitHub API tree
GITHUB_API_URL = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/git/trees/master?recursive=1"

def download_with_retry(url, dest, max_retries=3, chunk_size=8192):
    """Download a file with resume support and retries."""
    for attempt in range(max_retries):
        try:
            existing_size = os.path.getsize(dest) if os.path.exists(dest) else 0
            req = urllib.request.Request(url)
            if existing_size > 0:
                req.add_header('Range', f'bytes={existing_size}-')
            
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                total = resp.headers.get('Content-Length')
                if total:
                    total = int(total) + existing_size
                
                mode = 'ab' if existing_size > 0 else 'wb'
                downloaded = existing_size
                with open(dest, mode) as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded * 100 / total
                            print(f"\r  {downloaded // (1024*1024)} / {total // (1024*1024)} MB ({pct:.0f}%)", end="", flush=True)
                        else:
                            print(f"\r  {downloaded // (1024*1024)} MB", end="", flush=True)
                print()
            return True
        except Exception as e:
            print(f"\nAttempt {attempt+1}/{max_retries} failed: {e}")
            time.sleep(2 ** attempt)
    return False


def try_small_zip_download():
    """Try downloading just the segmented/color images from a smaller source."""
    # Try multiple alternative URLs
    alt_urls = [
        # Direct smaller dataset archives from various educational mirrors
        "https://data.mendeley.com/public-files/datasets/tywbtsjrjv/files/d5652a28-c1d8-4b76-97f3-72fb80f94efc/file_downloaded",
        # PlantVillage on Mendeley Data (official mirror)
    ]
    
    zip_path = os.path.join(DATASET_DIR, "plantvillage_color.zip")
    
    for url in alt_urls:
        print(f"Trying: {url[:80]}...")
        if download_with_retry(url, zip_path, max_retries=2):
            # Verify it's a valid zip
            try:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    names = zf.namelist()
                    print(f"Valid zip with {len(names)} entries")
                    return zip_path
            except zipfile.BadZipFile:
                print("Invalid zip file, trying next...")
                os.remove(zip_path)
    return None


def create_dataset_from_existing_model():
    """
    If we can't download, create a proper directory structure 
    with documented placeholders so training scripts know what to expect.
    """
    print("\n=== Creating dataset directory structure ===")
    
    class_names = [
        'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust',
        'Apple___healthy', 'Blueberry___healthy',
        'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)___Common_rust_', 'Corn_(maize)___Northern_Leaf_Blight',
        'Corn_(maize)___healthy', 'Grape___Black_rot',
        'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        'Grape___healthy', 'Orange___Haunglongbing_(Citrus_greening)',
        'Peach___Bacterial_spot', 'Peach___healthy',
        'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
        'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
        'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew',
        'Strawberry___Leaf_scorch', 'Strawberry___healthy',
        'Tomato___Bacterial_spot', 'Tomato___Early_blight',
        'Tomato___Late_blight', 'Tomato___Leaf_Mold',
        'Tomato___Septoria_leaf_spot',
        'Tomato___Spider_mites Two-spotted_spider_mite',
        'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
        'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
    ]
    
    for cls in class_names:
        cls_dir = os.path.join(EXTRACT_DIR, cls)
        os.makedirs(cls_dir, exist_ok=True)
    
    # Save class mapping
    mapping = {i: name for i, name in enumerate(class_names)}
    import json
    mapping_path = os.path.join(DATASET_DIR, "class_mapping.json")
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"Created {len(class_names)} class directories at {EXTRACT_DIR}")
    print(f"Class mapping saved to {mapping_path}")
    print("\nTo populate with real images, either:")
    print("  1. Download from Kaggle: kaggle datasets download -d vipoooool/new-plant-diseases-dataset")
    print("  2. Download from: https://github.com/spMohanty/PlantVillage-Dataset")
    print("  3. Download from Mendeley: https://data.mendeley.com/datasets/tywbtsjrjv/1")
    
    return EXTRACT_DIR


def try_github_chunked_download():
    """Download the PlantVillage dataset in smaller chunks to avoid connection drops."""
    zip_path = os.path.join(DATASET_DIR, "plantvillage_raw.zip")
    url = "https://github.com/spMohanty/PlantVillage-Dataset/archive/refs/heads/master.zip"
    
    print(f"Downloading {url}")
    print("Using chunked download with aggressive retry...")
    
    existing_size = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
    if existing_size > 0:
        print(f"Resuming from {existing_size // (1024*1024)} MB")
    
    max_retries = 10
    chunk_size = 1024 * 1024  # 1MB chunks
    
    for attempt in range(max_retries):
        try:
            existing_size = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            if existing_size > 0:
                req.add_header('Range', f'bytes={existing_size}-')
            
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                content_range = resp.headers.get('Content-Range')
                content_length = resp.headers.get('Content-Length')
                
                if content_range:
                    total = int(content_range.split('/')[-1])
                elif content_length:
                    total = int(content_length) + existing_size
                else:
                    total = None
                
                downloaded = existing_size
                with open(zip_path, 'ab' if existing_size > 0 else 'wb') as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            mb_done = downloaded / (1024*1024)
                            mb_total = total / (1024*1024)
                            pct = downloaded * 100 / total
                            print(f"\r  {mb_done:.0f} / {mb_total:.0f} MB ({pct:.1f}%)", end="", flush=True)
                        else:
                            print(f"\r  {downloaded // (1024*1024)} MB", end="", flush=True)
                
                print()
                
                # Check if download is complete
                final_size = os.path.getsize(zip_path)
                if total and final_size >= total:
                    print(f"Download complete: {final_size // (1024*1024)} MB")
                    # Verify zip
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zf:
                            print(f"Valid zip with {len(zf.namelist())} entries")
                            return zip_path
                    except zipfile.BadZipFile:
                        print("Zip verification failed!")
                        return None
                elif not total:
                    # No content-length, assume complete
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zf:
                            print(f"Valid zip with {len(zf.namelist())} entries")
                            return zip_path
                    except zipfile.BadZipFile:
                        print("Incomplete download, retrying...")
                        
        except Exception as e:
            print(f"\nAttempt {attempt+1}/{max_retries}: {e}")
            time.sleep(min(5, 2 ** attempt))
    
    final_size = os.path.getsize(zip_path) if os.path.exists(zip_path) else 0
    print(f"\nDownload incomplete after {max_retries} attempts. Got {final_size // (1024*1024)} MB")
    return None


def extract_dataset(zip_path):
    """Extract downloaded zip to dataset directory."""
    print(f"\nExtracting {zip_path}...")
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Find the color images directory
        members = zf.namelist()
        color_prefix = None
        for m in members:
            if '/raw/color/' in m and m.endswith('/'):
                parts = m.split('/raw/color/')
                if len(parts) == 2 and parts[1] and '/' not in parts[1].rstrip('/'):
                    if color_prefix is None:
                        color_prefix = m.split('/raw/color/')[0] + '/raw/color/'
                    break
        
        if not color_prefix:
            # Try segmented or just root level
            for m in members:
                if m.count('/') == 2 and m.endswith('.JPG'):
                    color_prefix = '/'.join(m.split('/')[:1]) + '/'
                    break
        
        extracted = 0
        for member in members:
            if color_prefix and member.startswith(color_prefix):
                # Extract with adjusted path
                relative = member[len(color_prefix):]
                if not relative:
                    continue
                target = os.path.join(EXTRACT_DIR, relative)
                if member.endswith('/'):
                    os.makedirs(target, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    with zf.open(member) as src, open(target, 'wb') as dst:
                        dst.write(src.read())
                    extracted += 1
                    if extracted % 500 == 0:
                        print(f"  Extracted {extracted} files...")
        
        print(f"Extracted {extracted} files to {EXTRACT_DIR}")
    
    # Count classes and images
    classes = sorted([d for d in os.listdir(EXTRACT_DIR) 
                     if os.path.isdir(os.path.join(EXTRACT_DIR, d))])
    total_images = sum(len([f for f in os.listdir(os.path.join(EXTRACT_DIR, c))
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                      for c in classes)
    
    print(f"\nDataset: {len(classes)} classes, {total_images} images")
    for c in classes:
        n = len([f for f in os.listdir(os.path.join(EXTRACT_DIR, c))
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        print(f"  {c}: {n} images")
    
    return EXTRACT_DIR


if __name__ == "__main__":
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    # Check if dataset already exists
    if os.path.isdir(EXTRACT_DIR):
        classes = [d for d in os.listdir(EXTRACT_DIR) 
                  if os.path.isdir(os.path.join(EXTRACT_DIR, d))]
        images_exist = any(
            len([f for f in os.listdir(os.path.join(EXTRACT_DIR, c))
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))]) > 0
            for c in classes
        ) if classes else False
        
        if images_exist:
            total = sum(len([f for f in os.listdir(os.path.join(EXTRACT_DIR, c))
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                       for c in classes)
            print(f"Dataset already exists: {len(classes)} classes, {total} images")
            sys.exit(0)
    
    # Try chunked GitHub download with resume
    zip_path = try_github_chunked_download()
    
    if zip_path:
        extract_dataset(zip_path)
    else:
        print("\n=== All download attempts failed ===")
        create_dataset_from_existing_model()
        print("\nThe existing pre-trained model will continue to be used.")
        print("Manual dataset download is required for retraining.")
