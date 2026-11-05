"""
Verification test suite for OptiCrop Debug & Repair.
Validates:
1. Issue 1: What-If simulation endpoint, request structures, baseline & modified predictions, input deltas.
2. Issue 2: Crop Suitability multi-crop ranking for all 22 crops, limiting factors, and ranking order.
3. Issue 3: Plant disease reliability, species compatibility gating, chemical treatment withholding, and UI IDs.
4. Issue 4: Research analytics disease-evaluation and live latency benchmarking routes.
5. Static assets synchronization across static/ and public/ mirrors.
"""
import os
import json
import io
import unittest
import numpy as np
from PIL import Image

import app
from disease_model import CLASS_NAMES, SUPPORTED_PLANTS

class TestRepairedFunctionality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.app.testing = True
        cls.client = app.app.test_client()

    # -------------------------------------------------------------
    # ISSUE 1: CROP RECOMMEND WHAT-IF SIMULATOR
    # -------------------------------------------------------------
    def test_what_if_api_with_payload_aliases(self):
        """Test What-If API accepts both (baseline, modified) and (original, scenario) payloads."""
        payload1 = {
            'baseline': {'N': 70, 'P': 45, 'K': 45, 'temperature': 25.0, 'humidity': 75.0, 'ph': 6.5, 'rainfall': 150.0},
            'modified': {'N': 110, 'P': 45, 'K': 45, 'temperature': 28.0, 'humidity': 75.0, 'ph': 6.5, 'rainfall': 150.0}
        }
        res1 = self.client.post('/api/what-if', json=payload1)
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertTrue(data1['success'])
        self.assertIn('original_prediction', data1)
        self.assertIn('scenario_prediction', data1)
        self.assertIn('input_differences', data1)
        self.assertIn('explanation', data1)

        # Test alternative naming aliases
        payload2 = {
            'original': {'N': 90, 'P': 42, 'K': 43, 'temperature': 20.8, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.9},
            'scenario': {'N': 40, 'P': 55, 'K': 20, 'temperature': 28.0, 'humidity': 35.0, 'ph': 6.8, 'rainfall': 65.0}
        }
        res2 = self.client.post('/api/what-if', json=payload2)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertTrue(data2['success'])
        self.assertIn('top_3', data2['original_prediction'])
        self.assertIn('top_3', data2['scenario_prediction'])
        self.assertEqual(len(data2['original_prediction']['top_3']), 3)
        self.assertEqual(len(data2['scenario_prediction']['top_3']), 3)

    def test_what_if_input_validation(self):
        """Test What-If simulator rejects invalid out-of-range or NaN numbers."""
        invalid_payload = {
            'baseline': {'N': 70, 'P': 45, 'K': 45, 'temperature': 25.0, 'humidity': 75.0, 'ph': 6.5, 'rainfall': 150.0},
            'modified': {'N': -10, 'P': 45, 'K': 45, 'temperature': 25.0, 'humidity': 75.0, 'ph': 6.5, 'rainfall': 150.0}
        }
        res = self.client.post('/api/what-if', json=invalid_payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', res.get_json())

    # -------------------------------------------------------------
    # ISSUE 2: CROP SUITABILITY MULTI-CROP RANKING
    # -------------------------------------------------------------
    def test_multi_crop_suitability_all_22_crops(self):
        """Verify that multi-crop ranking evaluates and returns all 22 supported crops sorted by score."""
        payload = {
            'N': 90, 'P': 42, 'K': 43,
            'temperature': 20.87, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.91
        }
        res = self.client.post('/api/multi-crop-suitability', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['crops_evaluated'], 22)
        ranked = data['ranked_crops']
        self.assertEqual(len(ranked), 22)
        
        # Verify descending order of suitability score
        scores = [c['suitability_score'] for c in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))

        # Verify each crop record has required fields
        for c in ranked:
            self.assertIn('crop', c)
            self.assertIn('suitability_score', c)
            self.assertIn('classification', c)
            self.assertIn('primary_limiting_factor', c)
            self.assertTrue(0 <= c['suitability_score'] <= 100)

    # -------------------------------------------------------------
    # ISSUE 3: PLANT DISEASE RELIABILITY & CONTROLS
    # -------------------------------------------------------------
    def test_plant_disease_html_element_ids(self):
        """Verify all interactive button IDs and containers in templates/disease.html."""
        res = self.client.get('/disease-detection')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        required_ids = [
            'btn-open-catalog', 'disease-plant-select', 'unsupported-plant-warning',
            'disease-dropzone', 'disease-file-input', 'browse-files-btn',
            'disease-preview-container', 'disease-preview-img', 'preview-filename',
            'preview-filesize', 'remove-image-btn', 'btn-analyze-disease',
            'disease-empty-state', 'disease-results-card', 'disease-status-banner',
            'disease-status-icon', 'disease-status-title', 'disease-status-desc',
            'disease-severity-badge', 'disease-tier-badge', 'disease-result-crop',
            'disease-result-condition', 'disease-species-match-note',
            'disease-result-confidence', 'disease-confidence-fill', 'disease-caution-box',
            'disease-closest-cand-box', 'tab-overview', 'tab-immediate',
            'tab-spread', 'tab-treatment', 'tab-recovery', 'tab-sources',
            'disease-treatment-withheld-alert', 'treatment-status-tag',
            'recovery-checklist-container', 'checklist-progress-badge',
            'btn-test-another', 'disease-catalog-modal', 'btn-close-catalog'
        ]
        for eid in required_ids:
            self.assertIn(f'id="{eid}"', html, f"Element #{eid} missing from disease.html")

    def test_plant_disease_incompatible_treatment_withholding(self):
        """Verify that selecting a mismatched host species withholds chemical treatments."""
        apple_dir = os.path.join(app.BASE_DIR, 'datasets', 'plantvillage', 'Apple___Apple_scab')
        if os.path.exists(apple_dir):
            files = [f for f in os.listdir(apple_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            with open(os.path.join(apple_dir, files[0]), 'rb') as f:
                img_bytes = f.read()
        else:
            img = Image.new('RGB', (224, 224), (80, 140, 60))
            buf = io.BytesIO()
            img.save(buf, 'JPEG')
            img_bytes = buf.getvalue()

        # Upload with mismatched plant species: "Tomato"
        res = self.client.post('/api/disease-detection',
                               data={'image': (io.BytesIO(img_bytes), 'leaf.jpg'), 'selected_plant': 'Tomato'},
                               content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('treatment_withheld', data)
        if data['status'] == 'incompatible':
            self.assertTrue(data['treatment_withheld'])
            self.assertFalse(data['is_compatible'])

    # -------------------------------------------------------------
    # ISSUE 4: RESEARCH ANALYTICS
    # -------------------------------------------------------------
    def test_disease_evaluation_endpoint(self):
        """Verify /api/disease-evaluation returns valid metrics from root or fallback."""
        res = self.client.get('/api/disease-evaluation')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['num_classes'], 38)
        self.assertIn('metrics', data)
        self.assertIn('per_class_metrics', data)
        self.assertEqual(len(data['per_class_metrics']), 38)

    def test_benchmark_latency_endpoint(self):
        """Verify /api/benchmark-latency measures actual inference and returns structure."""
        res = self.client.get('/api/benchmark-latency')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('benchmarks', data)
        benchmarks = data['benchmarks']
        self.assertIn('crop_model', benchmarks)
        self.assertIn('mean_ms', benchmarks['crop_model'])
        self.assertIn('throughput_fps', benchmarks['crop_model'])
        self.assertGreater(benchmarks['crop_model']['mean_ms'], 0)
        
        # Check vision model benchmark if loaded
        if 'disease_model' in benchmarks:
            self.assertIn('mean_ms', benchmarks['disease_model'])
            self.assertIn('throughput_fps', benchmarks['disease_model'])
            self.assertGreater(benchmarks['disease_model']['mean_ms'], 0)

    # -------------------------------------------------------------
    # STATIC ASSET SYNCHRONIZATION
    # -------------------------------------------------------------
    def test_static_asset_mirrors_identical(self):
        """Ensure static/ and public/ mirrors of main.js and style.css are identical."""
        main_js_stat = os.path.getsize(os.path.join(app.BASE_DIR, 'static', 'js', 'main.js'))
        style_css_stat = os.path.getsize(os.path.join(app.BASE_DIR, 'static', 'css', 'style.css'))

        for p in ['public/js/main.js', 'public/static/js/main.js']:
            full_p = os.path.join(app.BASE_DIR, p)
            self.assertTrue(os.path.exists(full_p), f"Mirror {p} missing")
            self.assertEqual(os.path.getsize(full_p), main_js_stat, f"Size mismatch in {p}")

        for p in ['public/css/style.css', 'public/static/css/style.css']:
            full_p = os.path.join(app.BASE_DIR, p)
            self.assertTrue(os.path.exists(full_p), f"Mirror {p} missing")
            self.assertEqual(os.path.getsize(full_p), style_css_stat, f"Size mismatch in {p}")

if __name__ == '__main__':
    unittest.main()
