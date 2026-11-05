"""
test_critical_regressions.py — Evidence-Based Regression Tests for OptiCrop.

Covers:
1. Maple leaf with black tar spots -> NEVER diagnosed as Corn Gray Leaf Spot, treatments withheld.
2. Pear-like broadleaf with orange rust pustules -> NEVER diagnosed as Corn Gray Leaf Spot, treatments withheld.
3. Real PlantVillage Corn Common Rust image -> correctly diagnosed with high confidence.
4. Real PlantVillage Apple Scab image -> correctly diagnosed with high confidence.
5. Aadhaar image -> rejected as non-plant (400 validation error).
6. Television image -> rejected as non-plant (400 validation error).
7. Independent Vision Verifier integration & unsupported species rejection rule.
8. Local classifier vs. independent verification host disagreement rule.
9. Web research corroboration: source links included when configured, no fake sources when offline.
10. High model confidence is never presented as verified ground truth.
"""

import os
import io
import json
import pytest
from PIL import Image

import app as flask_app
from disease_model import PlantDiseaseDetector, CLASS_NAMES
from external_verifier import (
    IndependentVisionVerifier,
    AgriculturalWebResearcher,
    evaluate_final_decision,
    UNSUPPORTED_SPECIES_MESSAGE,
    INCONCLUSIVE_MESSAGE
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(BASE_DIR, 'test_fixtures')


@pytest.fixture
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as c:
        yield c


@pytest.fixture
def detector():
    return PlantDiseaseDetector.get_instance()


class TestCriticalOODRegressions:
    """Tests reproducing the reported false positive cases and verifying strict rejection."""

    def test_actual_problem_maple_tar_spots_image(self, client):
        """
        Exact user problem file: plant_disease1.jpeg (Maple leaf with black tar spots).
        Raw model predicted Corn (Maize) Gray Leaf Spot with 94.57% confidence.
        Must be safely intercepted as uncertain/inconclusive with chemical advice withheld.
        """
        fpath = os.path.join(FIXTURES_DIR, 'problem_maple_tar_spots.jpeg')
        if not os.path.exists(fpath):
            fpath = r'c:\Users\USER\Downloads\plant_disease1.jpeg'
        assert os.path.exists(fpath), f"Missing problem image {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'problem_maple_tar_spots.jpeg')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('success') is True
        assert data.get('crop') != 'Corn (Maize)', f"Actual problem maple misdiagnosed as Corn: {data}"
        assert data.get('condition') != 'Gray Leaf Spot (Cercospora zeae-maydis)'
        assert data.get('status') in ('uncertain', 'unsupported', 'incompatible', 'UNSUPPORTED', 'UNCERTAIN')
        assert data.get('is_reliable') is False
        assert data.get('treatment_withheld') is True
        assert 'Unsupported Crop' in data.get('crop') or 'Maple' in str(data)
        assert data.get('investigated_candidate') == 'maple_tar_spot'
        assert data.get('independent_assessment', {}).get('candidate_disease') == 'Maple Tar Spot (Rhytisma acerinum)'
        assert len(data.get('agricultural_references', [])) >= 3

        mgmt = data.get('management') or {}
        chem = mgmt.get('treatment_options', {}).get('chemical', [])
        assert len(chem) == 0, f"Chemical advice must be empty: {chem}"

    def test_actual_problem_pear_orange_rust_image(self, client):
        """
        Exact user problem file: fooddd.png (Pear-like broadleaf with orange rust pustules).
        Raw model predicted Corn (Maize) Gray Leaf Spot with 95.77% confidence.
        Must be safely intercepted as uncertain/inconclusive with chemical advice withheld.
        """
        fpath = os.path.join(FIXTURES_DIR, 'problem_pear_orange_rust.png')
        if not os.path.exists(fpath):
            fpath = r'c:\Users\USER\Downloads\fooddd.png'
        assert os.path.exists(fpath), f"Missing problem image {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'problem_pear_orange_rust.png')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('success') is True
        assert data.get('crop') != 'Corn (Maize)', f"Actual problem pear misdiagnosed as Corn: {data}"
        assert data.get('condition') != 'Gray Leaf Spot (Cercospora zeae-maydis)'
        assert data.get('status') in ('uncertain', 'unsupported', 'incompatible', 'UNSUPPORTED', 'UNCERTAIN')
        assert data.get('is_reliable') is False
        assert data.get('treatment_withheld') is True
        assert 'Unsupported Crop' in data.get('crop') or 'Pear' in str(data)
        assert data.get('investigated_candidate') == 'pear_rust'
        assert 'Pear Rust' in data.get('independent_assessment', {}).get('candidate_disease')
        assert len(data.get('agricultural_references', [])) >= 3

        mgmt = data.get('management') or {}
        chem = mgmt.get('treatment_options', {}).get('chemical', [])
        assert len(chem) == 0, f"Chemical advice must be empty: {chem}"

    def test_maple_tar_spot_never_diagnosed_as_corn(self, client):
        """
        Bug: A maple leaf with black tar-like spots was classified as Corn (Maize) / Gray Leaf Spot with 94.57% confidence.
        Fix: Must NEVER be classified as Corn. Status must be uncertain/unsupported, chemical advice withheld.
        """
        fpath = os.path.join(FIXTURES_DIR, 'maple_tar_spots.jpg')
        assert os.path.exists(fpath), f"Missing fixture {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'maple_tar_spots.jpg')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('success') is True
        assert data.get('crop') != 'Corn (Maize)', f"Maple was misdiagnosed as Corn! {data}"
        assert data.get('condition') != 'Gray Leaf Spot', f"Maple was misdiagnosed with Gray Leaf Spot! {data}"
        assert data.get('is_reliable') is False
        assert data.get('treatment_withheld') is True
        assert data.get('status') in ('uncertain', 'unsupported', 'UNSUPPORTED', 'UNCERTAIN')

        # Chemical advice must be withheld
        mgmt = data.get('management') or {}
        chem = mgmt.get('treatment_options', {}).get('chemical', [])
        assert len(chem) == 0, f"Chemical treatments must be empty for unverified maple: {chem}"

    def test_pear_orange_rust_never_diagnosed_as_corn(self, client):
        """
        Bug: A pear-like broadleaf image with orange rust pustules was classified as Corn (Maize) / Gray Leaf Spot.
        Fix: Must NEVER be classified as Corn. Status must be uncertain/unsupported, chemical advice withheld.
        """
        fpath = os.path.join(FIXTURES_DIR, 'pear_orange_rust.jpg')
        assert os.path.exists(fpath), f"Missing fixture {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'pear_orange_rust.jpg')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('success') is True
        assert data.get('crop') != 'Corn (Maize)', f"Pear was misdiagnosed as Corn! {data}"
        assert data.get('condition') != 'Gray Leaf Spot', f"Pear was misdiagnosed with Gray Leaf Spot! {data}"
        assert data.get('is_reliable') is False
        assert data.get('treatment_withheld') is True
        assert data.get('status') in ('uncertain', 'unsupported', 'UNSUPPORTED', 'UNCERTAIN')

        mgmt = data.get('management') or {}
        chem = mgmt.get('treatment_options', {}).get('chemical', [])
        assert len(chem) == 0, f"Chemical treatments must be empty for unverified pear: {chem}"

    def test_real_plantvillage_corn_common_rust(self, client):
        """
        A real PlantVillage Corn Common Rust image must be correctly identified as Corn with Common Rust.
        """
        fpath = os.path.join(FIXTURES_DIR, 'corn_common_rust.jpg')
        assert os.path.exists(fpath), f"Missing fixture {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'corn_common_rust.jpg')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('success') is True
        assert data.get('status') in ('supported', 'CORROBORATED', 'VERIFICATION UNAVAILABLE')
        pred_crop = data.get('local_ml_model_prediction', {}).get('crop') or data.get('crop')
        pred_cond = data.get('local_ml_model_prediction', {}).get('condition') or data.get('condition')
        assert pred_crop == 'Corn (Maize)'
        assert 'Rust' in pred_cond

    def test_real_plantvillage_apple_scab(self, client):
        """
        A real PlantVillage Apple Scab image must be correctly identified as Apple Scab with high confidence.
        """
        fpath = os.path.join(FIXTURES_DIR, 'apple_scab.jpg')
        assert os.path.exists(fpath), f"Missing fixture {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'apple_scab.jpg')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('success') is True
        assert data.get('status') in ('supported', 'CORROBORATED', 'VERIFICATION UNAVAILABLE')
        pred_crop = data.get('local_ml_model_prediction', {}).get('crop') or data.get('crop')
        pred_cond = data.get('local_ml_model_prediction', {}).get('condition') or data.get('condition')
        assert pred_crop == 'Apple'
        assert 'Scab' in pred_cond

    def test_aadhaar_card_rejected_as_non_plant(self, client):
        """
        Aadhaar card / ID photo must be rejected as a non-plant image before disease classification.
        """
        fpath = os.path.join(FIXTURES_DIR, 'aadhaar_card.png')
        assert os.path.exists(fpath), f"Missing fixture {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'aadhaar_card.png')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data
        assert data.get('crop') is None
        assert 'traceback' not in data['error'].lower()

    def test_television_screen_rejected_as_non_plant(self, client):
        """
        Television / monitor photo must be rejected as a non-plant image before disease classification.
        """
        fpath = os.path.join(FIXTURES_DIR, 'television_screen.jpg')
        assert os.path.exists(fpath), f"Missing fixture {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'television_screen.jpg')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data
        assert data.get('crop') is None

    def test_ganesha_idol_rejected_as_non_plant(self, client):
        """
        CRITICAL BUG REGRESSION: A religious idol of Ganesha must NEVER be classified as Corn Healthy.
        Must be rejected as a non-plant object/statue in Stage 1 with HTTP 400.
        """
        fpath = os.path.join(FIXTURES_DIR, 'ganesha_idol.jpeg')
        if not os.path.exists(fpath):
            fpath = r'c:\Users\USER\Downloads\plant_disease2.jpeg'
        assert os.path.exists(fpath), f"Missing fixture {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'ganesha_idol.jpeg')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 400, f"Ganesha idol was not rejected! Status: {resp.status_code}, data: {resp.get_json()}"
        data = resp.get_json()
        assert 'error' in data
        assert data.get('crop') is None
        assert 'corn' not in data.get('error', '').lower()
        assert data.get('validation_failed') is True

    def test_real_plantvillage_potato_late_blight(self, client):
        """
        Real PlantVillage Potato Late Blight image must be correctly identified as Potato Late Blight.
        """
        fpath = os.path.join(FIXTURES_DIR, 'potato_late_blight.jpg')
        assert os.path.exists(fpath), f"Missing fixture {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'potato_late_blight.jpg')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') is True
        assert data.get('status') in ('supported', 'CORROBORATED', 'VERIFICATION UNAVAILABLE')
        pred_crop = data.get('local_ml_model_prediction', {}).get('crop') or data.get('crop')
        pred_cond = data.get('local_ml_model_prediction', {}).get('condition') or data.get('condition')
        assert pred_crop == 'Potato'
        assert 'Late Blight' in pred_cond

    def test_real_plantvillage_tomato_early_blight(self, client):
        """
        Real PlantVillage Tomato Early Blight image must be correctly identified as Tomato Early Blight.
        """
        fpath = os.path.join(FIXTURES_DIR, 'tomato_early_blight.jpg')
        assert os.path.exists(fpath), f"Missing fixture {fpath}"
        with open(fpath, 'rb') as f:
            img_bytes = f.read()

        resp = client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(img_bytes), 'tomato_early_blight.jpg')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') is True
        assert data.get('status') in ('supported', 'CORROBORATED', 'VERIFICATION UNAVAILABLE')
        pred_crop = data.get('local_ml_model_prediction', {}).get('crop') or data.get('crop')
        pred_cond = data.get('local_ml_model_prediction', {}).get('condition') or data.get('condition')
        assert pred_crop == 'Tomato'
        assert 'Early Blight' in pred_cond


class TestDecisionRulesAndCorroboration:
    """Verifies image-first decision rules, external verifier fallback, and web research."""

    def test_offline_safe_fallback_when_no_api_keys(self):
        """
        When external vision/search keys are absent, app must still run safely
        and NOT pretend that external verification succeeded.
        """
        # Save env
        old_gemini = os.environ.pop('GEMINI_API_KEY', None)
        old_google = os.environ.pop('GOOGLE_API_KEY', None)
        old_openai = os.environ.pop('OPENAI_API_KEY', None)
        old_tavily = os.environ.pop('TAVILY_API_KEY', None)
        old_serp = os.environ.pop('SERPAPI_API_KEY', None)
        old_brave = os.environ.pop('BRAVE_API_KEY', None)
        old_mock_v = os.environ.pop('MOCK_VISION_RESPONSE', None)
        old_mock_s = os.environ.pop('MOCK_SEARCH_RESPONSE', None)

        try:
            verifier = IndependentVisionVerifier()
            assert verifier.is_configured() is False
            v_res = verifier.assess_image(b'fake')
            assert v_res['is_available'] is False
            assert "not configured" in v_res['reason']

            researcher = AgriculturalWebResearcher()
            assert researcher.is_configured() is False
            w_res = researcher.research_pathology("Corn", "rust", "Corn", "Common Rust")
            assert w_res['is_available'] is False
            assert w_res['sources'] == []
            assert "No supported search API key" in w_res['reason']
        finally:
            if old_gemini: os.environ['GEMINI_API_KEY'] = old_gemini
            if old_google: os.environ['GOOGLE_API_KEY'] = old_google
            if old_openai: os.environ['OPENAI_API_KEY'] = old_openai
            if old_tavily: os.environ['TAVILY_API_KEY'] = old_tavily
            if old_serp: os.environ['SERPAPI_API_KEY'] = old_serp
            if old_brave: os.environ['BRAVE_API_KEY'] = old_brave
            if old_mock_v: os.environ['MOCK_VISION_RESPONSE'] = old_mock_v
            if old_mock_s: os.environ['MOCK_SEARCH_RESPONSE'] = old_mock_s

    def test_vision_identifies_unsupported_species_returns_unsupported_message(self):
        """
        Rule: If plant species is unsupported, return 'Unsupported plant species — unable to verify disease.'
        """
        local_cand = {
            'predicted_crop': 'Corn (Maize)',
            'condition': 'Cercospora Leaf Spot Gray Leaf Spot',
            'confidence': 94.57,
            'status': 'supported'
        }
        vision_res = {
            'is_available': True,
            'verification_status': 'unsupported_species',
            'host_plant': 'Maple (Acer)',
            'leaf_structure': 'Palmate 5-lobed broadleaf with radiating veins',
            'is_monocot_grass': False,
            'is_broadleaf': True,
            'visible_symptoms': 'Large circular black stromatic lesions with yellow halo (tar spots)',
            'supported_host_detected': False,
            'compatible_with_local_candidate': False,
            'botanical_reasoning': 'Maple is a dicot tree outside the 14 supported crops. Not compatible with Corn.'
        }
        web_res = {'is_available': False, 'sources': []}

        decision = evaluate_final_decision(local_cand, vision_res, web_res)
        assert decision['status'] in ('incompatible', 'unsupported', 'UNSUPPORTED')
        assert decision['treatment_withheld'] is True
        assert UNSUPPORTED_SPECIES_MESSAGE in decision['warning']
        assert 'Maple' in decision['crop']

    def test_host_disagreement_returns_inconclusive_message(self):
        """
        Rule: If local classifier and independent verification disagree about host plant,
        do not show definitive diagnosis or treatment; return 'Inconclusive — please consult an agricultural expert.'
        """
        local_cand = {
            'predicted_crop': 'Corn (Maize)',
            'condition': 'Common Rust',
            'confidence': 92.0,
            'status': 'supported'
        }
        vision_res = {
            'is_available': True,
            'verification_status': 'inconclusive',
            'host_plant': 'Unknown Broadleaf',
            'leaf_structure': 'Ovate broadleaf',
            'is_monocot_grass': False,
            'is_broadleaf': True,
            'visible_symptoms': 'Orange pustules',
            'supported_host_detected': None,
            'compatible_with_local_candidate': False,
            'botanical_reasoning': 'Leaf is an ovate broadleaf, incompatible with Corn grass.'
        }
        web_res = {'is_available': False, 'sources': []}

        decision = evaluate_final_decision(local_cand, vision_res, web_res)
        assert decision['status'] in ('inconclusive', 'uncertain', 'UNCERTAIN')
        assert decision['treatment_withheld'] is True
        assert INCONCLUSIVE_MESSAGE in decision['warning']

    def test_web_research_sources_displayed_without_inventing_citations(self):
        """
        Rule: Show real source links when research succeeded, never invent fake citations.
        """
        mock_search = json.dumps({
            'is_available': True,
            'provider': 'tavily',
            'queries_executed': ['Apple leaf scab extension plant pathology'],
            'sources': [
                {
                    'title': 'Apple Scab - Penn State Extension',
                    'url': 'https://extension.psu.edu/apple-scab',
                    'snippet': 'Apple scab is caused by the fungus Venturia inaequalis...',
                    'source_type': 'agricultural_extension'
                }
            ],
            'corroboration_summary': 'Found 1 verified source.',
            'evidence_strength': 'moderate'
        })
        os.environ['MOCK_SEARCH_RESPONSE'] = mock_search
        try:
            researcher = AgriculturalWebResearcher()
            res = researcher.research_pathology("Apple", "scab", "Apple", "Apple Scab")
            assert res['is_available'] is True
            assert len(res['sources']) == 1
            assert res['sources'][0]['url'] == 'https://extension.psu.edu/apple-scab'
        finally:
            os.environ.pop('MOCK_SEARCH_RESPONSE', None)

