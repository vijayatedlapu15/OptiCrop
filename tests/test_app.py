import subprocess
import time
import urllib.request
import json
import sys

import os

def run_tests():
    print("Starting Flask server for verification tests...")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    run_script = os.path.join(root_dir, "run.py") if os.path.exists(os.path.join(root_dir, "run.py")) else "app.py"
    port = 5025
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["PORT"] = str(port)
    server_process = subprocess.Popen(
        [sys.executable, run_script], 
        cwd=root_dir,
        env=env,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to spin up (polling with timeout)
    server_ready = False
    for _ in range(30):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(base_url, timeout=1) as res:
                if res.status == 200:
                    server_ready = True
                    break
        except Exception:
            pass
    if not server_ready:
        print("Warning: server took longer than 15s to respond, proceeding to tests...")
    
    success = True
    
    try:
        # Test 1: Home page
        print("\nTest 1: GET / ...")
        req = urllib.request.Request(base_url)
        with urllib.request.urlopen(req) as res:
            print("Status:", res.status)
            if res.status == 200:
                print("Test 1 SUCCESS!")
            else:
                print("Test 1 FAILED")
                success = False

        # Test 2: Scenario 1 - Crop Recommendation API
        print("\nTest 2: POST /api/recommend (Rice values) ...")
        recommend_data = {
            "N": 90.0, "P": 42.0, "K": 43.0,
            "temperature": 20.87, "humidity": 82.0,
            "ph": 6.5, "rainfall": 202.91
        }
        req = urllib.request.Request(
            f"{base_url}/api/recommend",
            data=json.dumps(recommend_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as res:
            print("Status:", res.status)
            data = json.loads(res.read().decode('utf-8'))
            print("Response:", data)
            if data.get('crop') == 'Rice' and res.status == 200:
                print("Test 2 SUCCESS!")
            else:
                print("Test 2 FAILED")
                success = False

        # Test 3: Scenario 2 - Crop Suitability API
        print("\nTest 3: POST /api/suitability (Maize, low Nitrogen) ...")
        suitability_data = {
            "crop": "maize",
            "N": 20.0, "P": 50.0, "K": 40.0,
            "temperature": 23.0, "humidity": 65.0,
            "ph": 6.0, "rainfall": 90.0
        }
        req = urllib.request.Request(
            f"{base_url}/api/suitability",
            data=json.dumps(suitability_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as res:
            print("Status:", res.status)
            data = json.loads(res.read().decode('utf-8'))
            print("Response overall score:", data.get('overall_score'))
            print("Nitrogen status details:", data.get('details', {}).get('N'))
            if res.status == 200 and 'overall_score' in data:
                print("Test 3 SUCCESS!")
            else:
                print("Test 3 FAILED")
                success = False

        # Test 4: Scenario 3 - Research Data API
        print("\nTest 4: GET /api/research-data ...")
        req = urllib.request.Request(f"{base_url}/api/research-data")
        with urllib.request.urlopen(req) as res:
            print("Status:", res.status)
            data = json.loads(res.read().decode('utf-8'))
            print("Crops count:", len(data.get('crops', [])))
            print("Soil groups present:", list(data.get('soil_groups', {}).keys()))
            if res.status == 200 and len(data.get('crops', [])) > 0:
                print("Test 4 SUCCESS!")
            else:
                print("Test 4 FAILED")
                success = False

    except Exception as e:
        print("An error occurred during verification:", e)
        success = False
    finally:
        print("\nStopping Flask server...")
        server_process.terminate()
        try:
            out, err = server_process.communicate(timeout=5)
            print("Flask server stopped.")
            if err:
                print("SERVER STDERR:\n", err)
            if out:
                print("SERVER STDOUT:\n", out)
        except subprocess.TimeoutExpired:
            server_process.kill()
            print("Flask server killed.")
            
    if success:
        print("\nALL AUTOMATED VERIFICATION TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\nSOME VERIFICATION TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
