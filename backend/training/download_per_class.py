"""
PlantVillage per-class downloader.
Downloads images class-by-class via GitHub API to avoid large zip failures.
Resumes from where it left off.
"""
import os
import sys
import json
import time
import ssl
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

TRAINING_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(TRAINING_DIR)
DATASET_DIR = os.path.join(BACKEND_DIR, "datasets", "plantvillage")

REPO = "spMohanty/PlantVillage-Dataset"
BRANCH = "master"
COLOR_PATH = "raw/color"

CTX = ssl.create_default_context()

def api_get(url, retries=3):
    """GET from GitHub API with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'OptiCrop-Downloader/1.0')
            with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def download_file(url, dest, retries=3):
    """Download a single file with retries."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'OptiCrop-Downloader/1.0')
            with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
                with open(dest, 'wb') as f:
                    f.write(resp.read())
            return True
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                return False

def get_class_dirs():
    """Get list of class directories from the repo."""
    url = f"https://api.github.com/repos/{REPO}/contents/{COLOR_PATH}?ref={BRANCH}"
    data = api_get(url)
    return [(d['name'], d['url']) for d in data if d['type'] == 'dir']

def download_class_images(class_name, api_url, max_images=None):
    """Download all images for a single class."""
    class_dir = os.path.join(DATASET_DIR, class_name)
    os.makedirs(class_dir, exist_ok=True)
    
    # Check existing images
    existing = set(f for f in os.listdir(class_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png')))
    
    # Get file list from API
    try:
        files = api_get(api_url)
    except Exception as e:
        print(f"  ERROR listing {class_name}: {e}")
        return len(existing), 0
    
    image_files = [f for f in files 
                   if f['type'] == 'file' and f['name'].lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if max_images:
        image_files = image_files[:max_images]
    
    # Skip already downloaded
    to_download = [f for f in image_files if f['name'] not in existing]
    
    if not to_download:
        return len(existing), 0
    
    downloaded = 0
    for f in to_download:
        dest = os.path.join(class_dir, f['name'])
        # Use download_url (raw content URL)
        raw_url = f.get('download_url', f['html_url'].replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/'))
        if download_file(raw_url, dest):
            downloaded += 1
        
        # Rate limit protection
        if downloaded % 20 == 0:
            time.sleep(0.5)
    
    return len(existing) + downloaded, downloaded

def main():
    max_per_class = None
    if len(sys.argv) > 1:
        try:
            max_per_class = int(sys.argv[1])
            print(f"Limiting to {max_per_class} images per class")
        except ValueError:
            pass
    
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    print("Fetching class list from GitHub API...")
    try:
        classes = get_class_dirs()
    except Exception as e:
        print(f"Failed to get class list: {e}")
        sys.exit(1)
    
    print(f"Found {len(classes)} classes\n")
    
    total_images = 0
    total_new = 0
    
    for i, (class_name, api_url) in enumerate(classes, 1):
        print(f"[{i}/{len(classes)}] {class_name}...", end=" ", flush=True)
        count, new = download_class_images(class_name, api_url, max_per_class)
        total_images += count
        total_new += new
        if new > 0:
            print(f"{count} images ({new} new)")
        else:
            print(f"{count} images (already complete)")
    
    print(f"\n{'='*60}")
    print(f"Dataset: {len(classes)} classes, {total_images} total images ({total_new} newly downloaded)")
    print(f"Location: {DATASET_DIR}")
    
    # Save class mapping
    mapping = {i: classes[i][0] for i in range(len(classes))}
    mapping_path = os.path.join(os.path.dirname(DATASET_DIR), "class_mapping.json")
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"Class mapping saved to {mapping_path}")

if __name__ == "__main__":
    main()
