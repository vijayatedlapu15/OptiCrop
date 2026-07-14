import subprocess
import time
import urllib.request
import json
import sys

def run_tests():
    print("Starting Flask server for verification tests...")
    server_process = subprocess.Popen(
        [sys.executable, "app.py"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for the server to spin up
    time.sleep(3)
    
    base_url = "http://127.0.0.1:5000"
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
            server_process.wait(timeout=5)
            print("Flask server stopped.")
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
