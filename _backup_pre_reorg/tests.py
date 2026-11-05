"""
Comprehensive test suite for OptiCrop using Flask test client.
Tests crop recommendation, suitability, disease detection, research analytics,
and page rendering without needing to start a live server.
"""
import os
import io
import json
import sys
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

# ============================================================
# Page Rendering Tests
# ============================================================
class TestPageRoutes:
    def test_dashboard(self, client):
        res = client.get('/')
        assert res.status_code == 200
        assert b'OptiCrop' in res.data

    def test_recommend_page(self, client):
        res = client.get('/recommend')
        assert res.status_code == 200

    def test_suitability_page(self, client):
        res = client.get('/suitability')
        assert res.status_code == 200

    def test_research_page(self, client):
        res = client.get('/research')
        assert res.status_code == 200

    def test_disease_page(self, client):
        res = client.get('/disease-detection')
        assert res.status_code == 200
        html = res.data.decode()
        # Verify critical JS hook IDs exist
        critical_ids = [
            'disease-dropzone', 'disease-file-input', 'browse-files-btn',
            'disease-preview-container', 'disease-preview-img',
            'btn-analyze-disease', 'disease-results-card'
        ]
        for eid in critical_ids:
            assert f'id="{eid}"' in html, f"Missing element id: {eid}"

# ============================================================
# Health / Status Tests
# ============================================================
class TestHealth:
    def test_health_endpoint(self, client):
        res = client.get('/api/health')
        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] in ('online', 'degraded')
        assert 'crop_recommendation_model' in data
        assert 'plant_disease_model' in data

    def test_crop_model_loaded(self, client):
        res = client.get('/api/health')
        data = res.get_json()
        assert data['crop_recommendation_model']['loaded'] is True
        assert data['crop_recommendation_model']['classes_count'] == 22

# ============================================================
# Crop Recommendation API Tests
# ============================================================
class TestCropRecommendation:
    RICE_INPUT = {
        "N": 90, "P": 42, "K": 43,
        "temperature": 20.87, "humidity": 82.0,
        "ph": 6.5, "rainfall": 202.9
    }

    def test_valid_recommendation(self, client):
        res = client.post('/api/recommend',
                          json=self.RICE_INPUT,
                          content_type='application/json')
        assert res.status_code == 200
        data = res.get_json()
        assert 'crop' in data
        assert 'confidence' in data
        assert 'top_crops' in data
        assert isinstance(data['confidence'], (int, float))
        assert data['confidence'] > 0

    def test_top3_structure(self, client):
        res = client.post('/api/recommend', json=self.RICE_INPUT,
                          content_type='application/json')
        data = res.get_json()
        top = data['top_crops']
        assert len(top) == 3
        for crop_entry in top:
            assert 'crop' in crop_entry
            assert 'confidence' in crop_entry
            assert 'suitability_score' in crop_entry

    def test_top3_descending_order(self, client):
        res = client.post('/api/recommend', json=self.RICE_INPUT,
                          content_type='application/json')
        data = res.get_json()
        top = data['top_crops']
        confs = [c['confidence'] for c in top]
        assert confs == sorted(confs, reverse=True), f"Top 3 not in descending order: {confs}"

    def test_primary_matches_top1(self, client):
        res = client.post('/api/recommend', json=self.RICE_INPUT,
                          content_type='application/json')
        data = res.get_json()
        assert data['crop'] == data['top_crops'][0]['crop']

    def test_rice_prediction(self, client):
        res = client.post('/api/recommend', json=self.RICE_INPUT,
                          content_type='application/json')
        data = res.get_json()
        assert data['crop'] == 'Rice'

    def test_missing_field(self, client):
        bad = {"N": 90, "P": 42}  # Missing fields
        res = client.post('/api/recommend', json=bad,
                          content_type='application/json')
        assert res.status_code == 400

    def test_out_of_range_nitrogen(self, client):
        bad = dict(self.RICE_INPUT)
        bad['N'] = 999
        res = client.post('/api/recommend', json=bad,
                          content_type='application/json')
        assert res.status_code == 400
        data = res.get_json()
        assert 'error' in data

    def test_negative_values(self, client):
        bad = dict(self.RICE_INPUT)
        bad['N'] = -10
        res = client.post('/api/recommend', json=bad,
                          content_type='application/json')
        assert res.status_code == 400

    def test_non_numeric_input(self, client):
        bad = dict(self.RICE_INPUT)
        bad['N'] = 'abc'
        res = client.post('/api/recommend', json=bad,
                          content_type='application/json')
        assert res.status_code == 400

    def test_suitability_in_response(self, client):
        res = client.post('/api/recommend', json=self.RICE_INPUT,
                          content_type='application/json')
        data = res.get_json()
        assert 'suitability_score' in data
        assert 'details' in data

# ============================================================
# Crop Suitability API Tests
# ============================================================
class TestCropSuitability:
    def test_valid_suitability(self, client):
        res = client.post('/api/suitability', json={
            "crop": "rice", "N": 80, "P": 40, "K": 40,
            "temperature": 25, "humidity": 80, "ph": 6.5, "rainfall": 200
        }, content_type='application/json')
        assert res.status_code == 200
        data = res.get_json()
        assert 'overall_score' in data
        assert 'details' in data
        assert 0 <= data['overall_score'] <= 100

    def test_invalid_crop(self, client):
        res = client.post('/api/suitability', json={
            "crop": "unicorn_fruit", "N": 50, "P": 50, "K": 50,
            "temperature": 25, "humidity": 70, "ph": 6.5, "rainfall": 100
        }, content_type='application/json')
        assert res.status_code == 404

    def test_suitability_details_structure(self, client):
        res = client.post('/api/suitability', json={
            "crop": "maize", "N": 20, "P": 50, "K": 40,
            "temperature": 23, "humidity": 65, "ph": 6.0, "rainfall": 90
        }, content_type='application/json')
        data = res.get_json()
        for param in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']:
            assert param in data['details']
            detail = data['details'][param]
            assert 'status' in detail
            assert 'score' in detail
            assert 'remediation' in detail

# ============================================================
# Research Analytics Tests
# ============================================================
class TestResearch:
    def test_research_data(self, client):
        res = client.get('/api/research-data')
        assert res.status_code == 200
        data = res.get_json()
        assert 'crops' in data
        assert 'correlation' in data
        assert 'soil_groups' in data
        assert len(data['crops']) == 22

    def test_model_evaluation(self, client):
        res = client.get('/api/model-evaluation')
        if res.status_code == 200:
            data = res.get_json()
            assert 'metrics' in data
            assert 'accuracy' in data['metrics']

    def test_disease_classes(self, client):
        res = client.get('/api/disease-classes')
        assert res.status_code == 200
        data = res.get_json()
        assert 'catalog' in data

    def test_compare_crops(self, client):
        res = client.get('/api/compare-crops?crop1=rice&crop2=maize')
        assert res.status_code == 200
        data = res.get_json()
        assert data['crop1'] == 'Rice'
        assert data['crop2'] == 'Maize'
        assert 'parameters' in data

    def test_compare_invalid_crop(self, client):
        res = client.get('/api/compare-crops?crop1=rice&crop2=invalidcrop')
        assert res.status_code == 400

# ============================================================
# Disease Detection API Tests
# ============================================================
class TestDiseaseDetection:
    def _make_test_image(self, fmt='JPEG', size=(224, 224), color=(34, 100, 34)):
        from PIL import Image
        img = Image.new('RGB', size, color)
        buf = io.BytesIO()
        img.save(buf, fmt)
        buf.seek(0)
        return buf

    def test_no_image(self, client):
        res = client.post('/api/disease-detection')
        assert res.status_code == 400

    def test_invalid_extension(self, client):
        buf = io.BytesIO(b"not an image")
        res = client.post('/api/disease-detection',
                          data={'image': (buf, 'test.txt')},
                          content_type='multipart/form-data')
        assert res.status_code == 400

    def test_valid_image(self, client):
        buf = self._make_test_image()
        res = client.post('/api/disease-detection',
                          data={'image': (buf, 'leaf.jpg')},
                          content_type='multipart/form-data')
        assert res.status_code == 200
        data = res.get_json()
        assert data.get('success') is True
        assert 'crop' in data
        assert 'condition' in data
        assert 'confidence' in data
        assert 'top_candidates' in data
        assert isinstance(data['confidence'], (int, float))
        assert 0 <= data['confidence'] <= 100

    def test_response_has_care_info(self, client):
        buf = self._make_test_image()
        res = client.post('/api/disease-detection',
                          data={'image': (buf, 'leaf.jpg')},
                          content_type='multipart/form-data')
        data = res.get_json()
        assert 'symptoms' in data
        assert 'care_recommendations' in data
        assert 'prevention' in data
        assert 'severity' in data

    def test_top_candidates_structure(self, client):
        buf = self._make_test_image()
        res = client.post('/api/disease-detection',
                          data={'image': (buf, 'leaf.jpg')},
                          content_type='multipart/form-data')
        data = res.get_json()
        candidates = data['top_candidates']
        assert len(candidates) == 3
        for c in candidates:
            assert 'class_name' in c
            assert 'crop' in c
            assert 'confidence' in c

    def test_png_image(self, client):
        buf = self._make_test_image(fmt='PNG')
        res = client.post('/api/disease-detection',
                          data={'image': (buf, 'leaf.png')},
                          content_type='multipart/form-data')
        assert res.status_code == 200

# ============================================================
# Export Tests
# ============================================================
class TestExport:
    def test_csv_export(self, client):
        res = client.get('/api/export/csv')
        assert res.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
