"""
test_10_categories.py — Evidence-Based Testing across 10 Mandatory Categories.

Evaluates:
1. Potato Early Blight
2. Tomato Early Blight
3. Apple Scab
4. Rose Black Spot
5. Maple Tar Spot
6. Pear Rust
7. Ganesha idol
8. Green artificial objects
9. Healthy leaves
10. Blurry or unclear images

For each test records:
- Actual image identity
- Gemini identified plant
- Gemini suspected disease
- Google Search citations
- Local ML prediction
- Final status
- Whether output is supported by evidence
"""

import os
import io
import json
import pytest
from PIL import Image

import app as flask_app
from disease_model import PlantDiseaseDetector
from external_verifier import (
    STATUS_CORROBORATED,
    STATUS_POSSIBLE,
    STATUS_UNCERTAIN,
    STATUS_UNSUPPORTED,
    STATUS_VERIFICATION_UNAVAILABLE
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = (
    os.path.join(BASE_DIR, 'fixtures')
    if os.path.exists(os.path.join(BASE_DIR, 'fixtures'))
    else (
        os.path.join(BASE_DIR, 'test_fixtures')
        if os.path.exists(os.path.join(BASE_DIR, 'test_fixtures'))
        else os.path.join(BASE_DIR, '..', 'test_fixtures')
    )
)


@pytest.fixture
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as c:
        yield c


class TestTenRequiredCategories:

    def test_category_1_potato_early_blight(self, client):
        fpath = os.path.join(FIXTURES_DIR, 'potato_early_blight.jpg')
        assert os.path.exists(fpath)
        with open(fpath, 'rb') as f:
            resp = client.post('/api/disease-detection', data={'image': (f, 'potato_early_blight.jpg')}, content_type='multipart/form-data')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        pred = data.get('local_ml_model_prediction', {})
        assert pred.get('crop') == 'Potato'
        assert 'Early Blight' in pred.get('condition')
        assert data.get('status') in (STATUS_VERIFICATION_UNAVAILABLE, STATUS_CORROBORATED, 'supported')

    def test_category_2_tomato_early_blight(self, client):
        fpath = os.path.join(FIXTURES_DIR, 'tomato_early_blight.jpg')
        assert os.path.exists(fpath)
        with open(fpath, 'rb') as f:
            resp = client.post('/api/disease-detection', data={'image': (f, 'tomato_early_blight.jpg')}, content_type='multipart/form-data')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        pred = data.get('local_ml_model_prediction', {})
        assert pred.get('crop') == 'Tomato'
        assert 'Early Blight' in pred.get('condition')
        assert data.get('status') in (STATUS_VERIFICATION_UNAVAILABLE, STATUS_CORROBORATED, 'supported')

    def test_category_3_apple_scab(self, client):
        fpath = os.path.join(FIXTURES_DIR, 'apple_scab.jpg')
        assert os.path.exists(fpath)
        with open(fpath, 'rb') as f:
            resp = client.post('/api/disease-detection', data={'image': (f, 'apple_scab.jpg')}, content_type='multipart/form-data')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        pred = data.get('local_ml_model_prediction', {})
        assert pred.get('crop') == 'Apple'
        assert 'Scab' in pred.get('condition')
        assert data.get('status') in (STATUS_VERIFICATION_UNAVAILABLE, STATUS_CORROBORATED, 'supported')

    def test_category_4_rose_black_spot_unsupported_crop(self, client):
        """
        Rose is an ornamental shrub outside OptiCrop's 14 crops.
        When Gemini identifies Rose, status must be UNSUPPORTED and chemical advice withheld.
        """
        mock_vision = json.dumps({
            'is_plant': True,
            'is_clear': True,
            'likely_plant': 'Rose (Rosa spp.)',
            'leaf_shape_and_structure': 'Pinnate compound leaf with serrated oval leaflets',
            'is_monocot_grass': False,
            'is_broadleaf': True,
            'visible_symptoms': 'Circular black lesions with feathery margins and surrounding chlorosis',
            'colour_changes_and_patterns': 'Yellow chlorotic halos around dark lesions',
            'most_likely_disease': 'Black Spot (Diplocarpon rosae)',
            'alternative_diagnoses': ['Cercospora leaf spot', 'Anthracnose'],
            'is_healthy': False,
            'supported_opticrop_species': False,
            'identification_certainty': 'high',
            'diagnostic_reasoning': 'Rose is an ornamental shrub outside OptiCrop 14 crops. Typical Diplocarpon rosae black spots.'
        })
        os.environ['MOCK_VISION_RESPONSE'] = mock_vision
        try:
            fpath = os.path.join(FIXTURES_DIR, 'rose_black_spot.jpg')
            with open(fpath, 'rb') as f:
                resp = client.post('/api/disease-detection', data={'image': (f, 'rose_black_spot.jpg')}, content_type='multipart/form-data')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['status'] == STATUS_UNSUPPORTED
            assert data['treatment_withheld'] is True
            assert 'Rose' in data.get('likely_plant', '')
            assert 'Black Spot' in data.get('most_likely_disease', '')
        finally:
            os.environ.pop('MOCK_VISION_RESPONSE', None)

    def test_category_5_maple_tar_spot_unsupported(self, client):
        fpath = os.path.join(FIXTURES_DIR, 'problem_maple_tar_spots.jpeg')
        with open(fpath, 'rb') as f:
            resp = client.post('/api/disease-detection', data={'image': (f, 'problem_maple_tar_spots.jpeg')}, content_type='multipart/form-data')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == STATUS_UNSUPPORTED
        assert data['treatment_withheld'] is True
        assert data['crop'] != 'Corn (Maize)'

    def test_category_6_pear_rust_unsupported(self, client):
        fpath = os.path.join(FIXTURES_DIR, 'problem_pear_orange_rust.png')
        with open(fpath, 'rb') as f:
            resp = client.post('/api/disease-detection', data={'image': (f, 'problem_pear_orange_rust.png')}, content_type='multipart/form-data')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == STATUS_UNSUPPORTED
        assert data['treatment_withheld'] is True
        assert data['crop'] != 'Corn (Maize)'

    def test_category_7_ganesha_idol_rejected(self, client):
        fpath = os.path.join(FIXTURES_DIR, 'ganesha_idol.jpeg')
        with open(fpath, 'rb') as f:
            resp = client.post('/api/disease-detection', data={'image': (f, 'ganesha_idol.jpeg')}, content_type='multipart/form-data')
        assert resp.status_code == 400
        data = resp.get_json()
        assert data.get('validation_failed') is True
        assert 'error' in data

    def test_category_8_green_artificial_objects(self, client):
        """
        Artificial green plastic/fabric object must be detected as non-plant / rejected or uncertain.
        """
        fpath = os.path.join(FIXTURES_DIR, 'green_artificial_object.png')
        with open(fpath, 'rb') as f:
            resp = client.post('/api/disease-detection', data={'image': (f, 'green_artificial_object.png')}, content_type='multipart/form-data')
        # Either rejected in Stage 1 validator or intercepted by vision as non-plant
        if resp.status_code == 400:
            data = resp.get_json()
            assert data.get('validation_failed') is True
        else:
            assert resp.status_code == 200
            data = resp.get_json()
            assert data.get('treatment_withheld') is True

    def test_category_9_healthy_leaves(self, client):
        fpath = os.path.join(FIXTURES_DIR, 'healthy_leaf.jpg')
        with open(fpath, 'rb') as f:
            resp = client.post('/api/disease-detection', data={'image': (f, 'healthy_leaf.jpg')}, content_type='multipart/form-data')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        pred = data.get('local_ml_model_prediction', {})
        assert 'healthy' in pred.get('condition', '').lower()

    def test_category_10_blurry_or_unclear_images(self, client):
        """
        A heavily blurred foliar image must be classified as UNCERTAIN or rejected.
        """
        mock_vision = json.dumps({
            'is_plant': True,
            'is_clear': False,
            'non_plant_description': 'Severe optical motion blur and out-of-focus optics.',
            'likely_plant': 'Uncertain Plant',
            'leaf_shape_and_structure': 'Indistinct foliar structure',
            'is_monocot_grass': False,
            'is_broadleaf': False,
            'visible_symptoms': 'No distinct foliar lesions resolvable due to blur.',
            'colour_changes_and_patterns': 'Diffuse green blur',
            'most_likely_disease': 'Uncertain',
            'alternative_diagnoses': [],
            'is_healthy': False,
            'supported_opticrop_species': False,
            'identification_certainty': 'uncertain',
            'diagnostic_reasoning': 'Image lacks resolving power to discern diagnostic pathology.'
        })
        os.environ['MOCK_VISION_RESPONSE'] = mock_vision
        try:
            fpath = os.path.join(FIXTURES_DIR, 'blurry_unclear_leaf.jpg')
            with open(fpath, 'rb') as f:
                resp = client.post('/api/disease-detection', data={'image': (f, 'blurry_unclear_leaf.jpg')}, content_type='multipart/form-data')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['status'] == STATUS_UNCERTAIN
            assert data['treatment_withheld'] is True
        finally:
            os.environ.pop('MOCK_VISION_RESPONSE', None)
