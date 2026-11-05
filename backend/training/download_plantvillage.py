"""Download PlantVillage dataset with resume support."""
import os
import sys
import urllib.request
import zipfile
import shutil

TRAINING_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(TRAINING_DIR)
ROOT_DIR = os.path.dirname(BACKEND_DIR)

DATASET_DIR = os.path.join(BACKEND_DIR, "datasets", "plantvillage")
ZIP_PATH = os.path.join(BACKEND_DIR, "datasets", "plantvillage_raw.zip")

# Alternative sources - using smaller color-only subset
URLS = [
    # Direct color images from PlantVillage repo
    "https://github.com/spMohanty/PlantVillage-Dataset/archive/refs/heads/master.zip",
]

def download_with_resume():
    os.makedirs(os.path.join(BACKEND_DIR, "datasets"), exist_ok=True)
    
    if os.path.exists(DATASET_DIR) and len([d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]) > 10:
        print(f"Dataset already exists with class directories. Skipping download.")
        return True
    
    existing_size = 0
    if os.path.exists(ZIP_PATH):
        existing_size = os.path.getsize(ZIP_PATH)
        print(f"Resuming download from {existing_size / 1024 / 1024:.1f} MB")
    
    for url in URLS:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            })
            if existing_size > 0:
                req.add_header("Range", f"bytes={existing_size}-")
            
            resp = urllib.request.urlopen(req, timeout=300)
            
            total = resp.headers.get("Content-Length")
            is_partial = resp.status == 206
            
            if total:
                total = int(total)
                if is_partial:
                    total += existing_size
            
            mode = 'ab' if is_partial else 'wb'
            downloaded = existing_size if is_partial else 0
            
            print(f"Downloading: {url}")
            if total:
                print(f"Total expected: {total / 1024 / 1024:.1f} MB")
            
            with open(ZIP_PATH, mode) as f:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        sys.stdout.write(f"\r  {downloaded / 1024 / 1024:.0f} / {total / 1024 / 1024:.0f} MB ({pct:.0f}%)")
                    else:
                        sys.stdout.write(f"\r  {downloaded / 1024 / 1024:.0f} MB")
                    sys.stdout.flush()
            
            final_size = os.path.getsize(ZIP_PATH)
            print(f"\nDownload complete: {final_size / 1024 / 1024:.1f} MB")
            return True
            
        except Exception as e:
            print(f"\nDownload error: {e}")
            print(f"Downloaded so far: {os.path.getsize(ZIP_PATH) / 1024 / 1024:.1f} MB (will resume on next run)")
    
    return False

def extract():
    if not os.path.exists(ZIP_PATH):
        print("No zip file found.")
        return False
    
    print(f"Extracting {ZIP_PATH} ({os.path.getsize(ZIP_PATH) / 1024 / 1024:.1f} MB)...")
    temp_dir = os.path.join(BACKEND_DIR, "datasets", "_temp_extract")
    
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
            zf.extractall(temp_dir)
    except zipfile.BadZipFile:
        print("ERROR: Zip file is corrupted or incomplete. Deleting and retry needed.")
        os.remove(ZIP_PATH)
        return False
    
    # Find the color directory with 38 class folders
    for root, dirs, files in os.walk(temp_dir):
        class_dirs = [d for d in dirs if "___" in d]
        if len(class_dirs) >= 30:
            print(f"Found {len(class_dirs)} class directories in: {root}")
            os.makedirs(DATASET_DIR, exist_ok=True)
            for d in sorted(dirs):
                src = os.path.join(root, d)
                if os.path.isdir(src):
                    dst = os.path.join(DATASET_DIR, d)
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
            break
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    os.remove(ZIP_PATH)
    print("Extraction complete, temp files cleaned up.")
    return True

def verify():
    if not os.path.exists(DATASET_DIR):
        return False
    
    classes = sorted([d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))])
    total = 0
    for cls in classes:
        n = len([f for f in os.listdir(os.path.join(DATASET_DIR, cls)) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        total += n
        print(f"  {cls}: {n} images")
    
    print(f"\nTotal: {len(classes)} classes, {total} images")
    return len(classes) >= 30

if __name__ == "__main__":
    if not download_with_resume():
        print("Download failed. Will retry on next run.")
        sys.exit(1)
    if not extract():
        sys.exit(1)
    verify()
