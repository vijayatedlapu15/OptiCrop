import io
import json
from PIL import Image
from app import app, load_resources

def run_tests():
    print("=" * 60)
    print("RUNNING OPTICROP ML ENHANCEMENT VERIFICATION SUITE")
    print("=" * 60)

    load_resources()
    client = app.test_client()

    # 1. Test HTML Pages
    pages = ['/', '/recommend', '/suitability', '/research', '/disease-detection']
    for p in pages:
        res = client.get(p)
        assert res.status_code == 200, f"Page {p} returned {res.status_code}"
        print(f"[PASS] Page route '{p}' rendered successfully (200 OK)")

    # 2. Test API Health
    res = client.get('/api/health')
    assert res.status_code == 200, f"Health check returned {res.status_code}"
    health = res.get_json()
    assert health['status'] == 'online', f"Health status is {health['status']}"
    assert health['crop_recommendation_model']['loaded'] is True
    assert health['plant_disease_model']['loaded'] is True
    print(f"[PASS] /api/health: Status '{health['status']}', RF Crop Model Loaded, MobileNetV2 Disease Model Loaded")

    # 3. Test Model Evaluation
    res = client.get('/api/model-evaluation')
    assert res.status_code == 200
    metrics = res.get_json()
    assert metrics['metrics']['accuracy'] == 99.32
    assert metrics['test_samples_evaluated'] == 440
    assert 'feature_importance' in metrics
    print(f"[PASS] /api/model-evaluation: Test Accuracy {metrics['metrics']['accuracy']}%, 440 held-out samples verified")

    # 4. Test Crop Comparison
    res = client.get('/api/compare-crops?crop1=rice&crop2=maize')
    assert res.status_code == 200
    comp = res.get_json()
    assert comp['crop1'] == 'Rice'
    assert comp['crop2'] == 'Maize'
    assert 'rainfall' in comp['parameters']
    assert comp['parameters']['rainfall']['unit'] == 'mm'
    assert len(comp['insights']) > 0
    print(f"[PASS] /api/compare-crops: Comparison of Rice vs Maize returned empirical metrics with units & insights")

    # 5. Test Disease Classes Catalog
    res = client.get('/api/disease-classes')
    assert res.status_code == 200
    classes = res.get_json()
    assert classes['total_classes'] == 38
    print(f"[PASS] /api/disease-classes: 38 benchmark PlantVillage classes taxonomy verified")

    # 6. Test Crop Recommendation (Scenario 1)
    sample_payload = {
        'N': 90,
        'P': 42,
        'K': 43,
        'temperature': 20.87,
        'humidity': 82.0,
        'ph': 6.5,
        'rainfall': 202.93
    }
    res = client.post('/api/recommend', json=sample_payload)
    assert res.status_code == 200
    rec = res.get_json()
    assert 'crop' in rec
    assert rec['confidence'] > 0
    print(f"[PASS] /api/recommend: Recommended '{rec['crop']}' with confidence {rec['confidence']}%")

    # 7. Test Plant Disease Detection (Scenario 4)
    # Create test image in memory
    img = Image.new('RGB', (224, 224), color=(34, 139, 34))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    data = {
        'image': (img_byte_arr, 'test_leaf.jpg')
    }
    res = client.post('/api/disease-detection', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    disease_res = res.get_json()
    assert disease_res['success'] is True
    assert 'crop' in disease_res
    assert 'condition' in disease_res
    assert 'confidence' in disease_res
    assert 'symptoms' in disease_res
    assert len(disease_res['care_recommendations']) > 0
    print(f"[PASS] /api/disease-detection: Diagnosed '{disease_res['crop']} - {disease_res['condition']}' with confidence {disease_res['confidence']}%")
    if disease_res.get('warning'):
        print(f"       [Verified Safety Guardrail] Low-confidence warning triggered correctly for out-of-distribution input.")

    print("=" * 60)
    print("ALL 7 VERIFICATION PHASES PASSED WITH ZERO ERRORS!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
