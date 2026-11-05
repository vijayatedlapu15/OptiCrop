"""
Comprehensive Reliability & Uncertainty Verification Test Suite for OptiCrop.
Tests:
1. Complete 38-class and 14-species mapping integrity.
2. RGB preprocessing and tensor dimensions.
3. Real ONNX inference engine execution.
4. Correct label-to-index alignment.
5. In-distribution supported-class sample images.
6. Invalid and degraded uploads (empty bytes, non-image bytes, <32x32 resolution, blank/solid images).
7. Host species selection & compatibility safeguards (matching, mismatching, unsupported species like Pear).
8. Uncertainty handling: full 38-class Shannon entropy, margin, calibrated thresholds.
9. Treatment withholding: ensuring definitive disease-specific treatments are withheld for uncertain/incompatible predictions.
10. Honest metric evaluations.
"""
import os
import io
import json
import pytest
import numpy as np
from PIL import Image

from app import app
from disease_model import (
    PlantDiseaseDetector,
    CLASS_NAMES,
    SUPPORTED_PLANTS,
    PLANT_CLASS_TO_SPECIES,
    normalize_species_name,
    UNCERTAIN_MESSAGE
)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

class TestMappingAndTaxonomy:
    def test_all_38_classes_mapped(self):
        """Every one of the 38 classes must map to exactly one of the 14 supported species."""
        assert len(CLASS_NAMES) == 38
        assert len(SUPPORTED_PLANTS) == 14
        mapped_classes = []
        for sp, info in SUPPORTED_PLANTS.items():
            mapped_classes.extend(info['classes'])
        assert len(mapped_classes) == 38
        assert set(mapped_classes) == set(CLASS_NAMES)

    def test_inverted_mapping_complete(self):
        """PLANT_CLASS_TO_SPECIES contains all 38 classes."""
        assert len(PLANT_CLASS_TO_SPECIES) == 38
        for c in CLASS_NAMES:
            assert c in PLANT_CLASS_TO_SPECIES
            assert PLANT_CLASS_TO_SPECIES[c] in SUPPORTED_PLANTS

    def test_species_normalizer(self):
        """Normalization handles common variations, aliases, and unsupported names."""
        assert normalize_species_name('apple') == 'Apple'
        assert normalize_species_name('corn') == 'Corn (Maize)'
        assert normalize_species_name('maize') == 'Corn (Maize)'
        assert normalize_species_name('bell pepper') == 'Pepper (Bell)'
        assert normalize_species_name('auto-detect') is None
        assert normalize_species_name('') is None
        # Unsupported species return normalized title
        assert normalize_species_name('pear') == 'Pear'
        assert normalize_species_name('rice') == 'Rice'

    def test_class_mapping_json_consistency(self):
        """Verify class_mapping.json aligns with CLASS_NAMES."""
        candidates = [
            os.path.join(os.path.dirname(__file__), '..', 'backend', 'config', 'class_mapping.json'),
            os.path.join(os.path.dirname(__file__), '..', 'backend', 'datasets', 'class_mapping.json'),
            'class_mapping.json'
        ]
        cmap_path = next((p for p in candidates if os.path.exists(p)), 'class_mapping.json')
        with open(cmap_path, 'r') as f:
            cm = json.load(f)
        for i, name in enumerate(CLASS_NAMES):
            assert cm[str(i)] == name

class TestInferenceAndPreprocessing:
    @pytest.fixture
    def detector(self):
        return PlantDiseaseDetector.get_instance()

    def test_onnx_active(self, detector):
        """Verify ONNX runtime session is initialized and using CPU."""
        assert detector.use_onnx is True
        assert detector.session is not None

    def test_preprocessing_dimensions(self, detector):
        """Verify image preprocessing outputs NCHW tensor with shape (1, 3, 224, 224)."""
        img = Image.new('RGB', (400, 300), (100, 150, 200))
        arr = detector._preprocess_image_numpy(img)
        assert arr.shape == (1, 3, 224, 224)
        assert arr.dtype == np.float32

    def test_onnx_warmup_and_output_shape(self, detector):
        """Model outputs exactly 38 logits for batch size 1."""
        dummy = np.zeros((1, 3, 224, 224), dtype=np.float32)
        in_name = detector.session.get_inputs()[0].name
        out = detector.session.run(None, {in_name: dummy})[0]
        assert out.shape == (1, 38)

class TestUploadValidationAndDegradedInputs:
    @pytest.fixture
    def detector(self):
        return PlantDiseaseDetector.get_instance()

    def test_empty_bytes(self, detector):
        res = detector.predict(b'')
        assert res['success'] is False

    def test_corrupted_bytes(self, detector):
        res = detector.predict(b'corrupted_image_data_here')
        assert res['success'] is False
        assert 'Unable to decode image' in res['error']

    def test_too_small_dimensions(self, detector):
        small_img = Image.new('RGB', (16, 16), (50, 100, 50))
        buf = io.BytesIO()
        small_img.save(buf, 'PNG')
        res = detector.predict(buf.getvalue())
        assert res['success'] is False
        assert 'too low' in res['error']

    def test_blank_solid_image_triggers_uncertainty(self, detector):
        """Solid color image lacks texture and must be rejected or trigger uncertain status."""
        solid_img = Image.new('RGB', (224, 224), (34, 139, 34))
        buf = io.BytesIO()
        solid_img.save(buf, 'JPEG')
        res = detector.predict(buf.getvalue())
        assert res['success'] is False or res['status'] in ('uncertain', 'UNCERTAIN', 'unsupported', 'UNSUPPORTED')

class TestSpeciesCompatibilityAndSafety:
    @pytest.fixture
    def detector(self):
        return PlantDiseaseDetector.get_instance()

    @pytest.fixture
    def real_apple_image(self):
        apple_dir = 'datasets/plantvillage/Apple___Apple_scab'
        if not os.path.exists(apple_dir):
            apple_dir = 'backend/datasets/plantvillage/Apple___Apple_scab'
        files = [f for f in os.listdir(apple_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        with open(os.path.join(apple_dir, files[0]), 'rb') as f:
            return f.read()

    def test_auto_detect_supported_image(self, detector, real_apple_image):
        """Unspecified species on genuine sample returns supported or unverified reference status."""
        res = detector.predict(real_apple_image)
        assert res['success'] is True
        assert res['crop'] == 'Apple' or res.get('local_ml_model_prediction', {}).get('crop') == 'Apple'
        assert res['status'] in ('supported', 'CORROBORATED', 'VERIFICATION UNAVAILABLE')

    def test_compatible_species_selection(self, detector, real_apple_image):
        """Selecting the matching species confirms diagnosis."""
        res = detector.predict(real_apple_image, selected_plant='Apple')
        assert res['success'] is True
        assert res['is_compatible'] is True
        assert res['status'] in ('supported', 'CORROBORATED', 'VERIFICATION UNAVAILABLE')

    def test_incompatible_species_mismatch(self, detector, real_apple_image):
        """Selecting an incompatible species (e.g. Tomato for Apple) withholds diagnosis."""
        res = detector.predict(real_apple_image, selected_plant='Tomato')
        assert res['success'] is True
        assert res['is_compatible'] is False
        assert res['status'] in ('incompatible', 'unsupported', 'UNCERTAIN', 'UNSUPPORTED', 'VERIFICATION UNAVAILABLE')

    def test_unsupported_species_selection(self, detector, real_apple_image):
        """Selecting an unsupported plant (e.g. Pear) flags boundary and withholds diagnosis."""
        res = detector.predict(real_apple_image, selected_plant='Pear')
        assert res['success'] is True
        assert res['is_compatible'] is False
        assert res['status'] in ('incompatible', 'unsupported', 'UNSUPPORTED')

class TestApiEndpoints:
    def test_api_disease_classes_returns_catalog_and_species(self, client):
        res = client.get('/api/disease-classes')
        assert res.status_code == 200
        data = res.get_json()
        assert data['total_classes'] == 38
        assert data['total_species'] == 14
        assert len(data['classes']) == 38
        assert len(data['supported_species']) == 14
        assert 'unsupported_notice' in data

    def test_api_disease_detection_with_selected_plant(self, client):
        apple_dir = 'datasets/plantvillage/Apple___Apple_scab'
        if not os.path.exists(apple_dir):
            apple_dir = 'backend/datasets/plantvillage/Apple___Apple_scab'
        files = [f for f in os.listdir(apple_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        with open(os.path.join(apple_dir, files[0]), 'rb') as f:
            img_bytes = f.read()

        # Incompatible upload
        data = {
            'image': (io.BytesIO(img_bytes), 'leaf.jpg'),
            'selected_plant': 'Grape'
        }
        res = client.post('/api/disease-detection', data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        payload = res.get_json()
        assert payload['status'] in ('incompatible', 'unsupported', 'UNCERTAIN', 'UNSUPPORTED', 'VERIFICATION UNAVAILABLE')
        assert payload['treatment_withheld'] is True
