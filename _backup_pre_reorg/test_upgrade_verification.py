"""
Comprehensive Verification Suite for OptiCrop Advanced Agricultural Intelligence Upgrade
Tests all upgraded endpoints, navigation integrity, and safeguards.
"""
import unittest
import json
import io
import numpy as np
from PIL import Image

import app
from disease_kb import DISEASE_MANAGEMENT_KB, get_disease_management
from disease_model import CLASS_NAMES, SUPPORTED_PLANTS

class TestUpgradeFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.app.testing = True
        cls.client = app.app.test_client()

    def test_canonical_five_sections_only(self):
        """Verify that exactly the five canonical sections exist in navigation."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        # Verify 5 sidebar routes
        expected_routes = ['/', '/recommend', '/suitability', '/disease-detection', '/research']
        for route in expected_routes:
            self.assertIn(f'href="{route}"', html, f"Canonical route {route} must exist in sidebar")
        # Ensure no unexpected route is added to sidebar navigation
        self.assertNotIn('href="/simulator"', html)
        self.assertNotIn('href="/knowledge-base"', html)
        self.assertNotIn('href="/treatment"', html)

    def test_all_five_pages_render_200(self):
        """Ensure all 5 canonical page routes render with HTTP 200 OK."""
        pages = ['/', '/recommend', '/suitability', '/disease-detection', '/research']
        for p in pages:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"Page {p} failed to render")

    def test_farm_health_summary_api(self):
        """Test Smart Farm Health & Risk Summary API calculation."""
        payload = {
            'N': 90, 'P': 42, 'K': 43,
            'ph': 6.5, 'temperature': 20.8, 'humidity': 82.0, 'rainfall': 202.9
        }
        res = self.client.post('/api/farm-health-summary',
                               data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['has_data'])
        self.assertIn('health_score', data)
        self.assertTrue(0 <= data['health_score'] <= 100)
        self.assertIn('health_rating', data)
        self.assertIn('nutrients', data)
        self.assertIn('N', data['nutrients'])
        self.assertIn('P', data['nutrients'])
        self.assertIn('K', data['nutrients'])
        self.assertIn('ph', data)
        self.assertIn('climate', data)
        self.assertIn('alerts', data)
        self.assertIn('prioritized_actions', data)
        self.assertIn('methodology', data)

    def test_what_if_simulator_api(self):
        """Test What-If Scenario Simulator with real Random Forest inference."""
        payload = {
            'baseline': {
                'N': 90, 'P': 42, 'K': 43,
                'temperature': 20.8, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.9
            },
            'modified': {
                'N': 40, 'P': 55, 'K': 20,
                'temperature': 28.0, 'humidity': 35.0, 'ph': 6.8, 'rainfall': 65.0
            }
        }
        res = self.client.post('/api/what-if',
                               data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('original_prediction', data)
        self.assertIn('scenario_prediction', data)
        self.assertIn('input_differences', data)
        self.assertIn('explanation', data)
        self.assertIn('statistical_disclaimer', data)
        # Verify differences detected
        self.assertGreater(len(data['input_differences']), 0)
        # Verify explanation has key drivers
        self.assertIn('key_drivers', data['explanation'])
        self.assertGreater(len(data['explanation']['key_drivers']), 0)

    def test_what_if_validation_rejection(self):
        """Test What-If simulator rejects invalid out-of-range inputs."""
        payload = {
            'baseline': {'N': 90, 'P': 42, 'K': 43, 'temperature': 20.8, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.9},
            'modified': {'N': 9999, 'P': 42, 'K': 43, 'temperature': 20.8, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.9}
        }
        res = self.client.post('/api/what-if',
                               data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn('error', data)

    def test_multi_crop_suitability_api(self):
        """Test Explainable Multi-Crop Comparison & Ranking API."""
        payload = {
            'N': 90, 'P': 42, 'K': 43,
            'temperature': 20.8, 'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.9
        }
        res = self.client.post('/api/multi-crop-suitability',
                               data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total_crops_evaluated'], 22)
        self.assertEqual(len(data['ranked_crops']), 22)
        # Verify first ranked crop has score >= last ranked crop
        top_crop = data['ranked_crops'][0]
        bottom_crop = data['ranked_crops'][-1]
        self.assertGreaterEqual(top_crop['suitability_score'], bottom_crop['suitability_score'])
        # Verify limiting factors are identified
        self.assertIn('primary_limiting_factor', top_crop)
        self.assertIn('scoring_methodology', data)

    def test_disease_kb_coverage(self):
        """Test that all 38 benchmark PlantVillage classes have structured KB entries."""
        self.assertEqual(len(CLASS_NAMES), 38)
        for class_name in CLASS_NAMES:
            self.assertIn(class_name, DISEASE_MANAGEMENT_KB, f"Missing KB entry for class: {class_name}")
            entry = DISEASE_MANAGEMENT_KB[class_name]
            self.assertIn('crop', entry)
            self.assertIn('condition', entry)
            self.assertIn('pathogen_type', entry)
            self.assertIn('causal_agent', entry)
            self.assertIn('immediate_actions', entry)
            self.assertIn('spread_prevention', entry)
            self.assertIn('cultural_management', entry)
            self.assertIn('treatment_options', entry)
            self.assertIn('recovery_monitoring', entry)
            self.assertIn('prevention_next_cycle', entry)
            self.assertIn('expert_assistance', entry)
            self.assertIn('references', entry)
            self.assertGreater(len(entry['references']), 0)

    def test_treatment_withholding_on_uncertainty(self):
        """Ensure chemical treatments are strictly withheld when prediction is uncertain."""
        # For Early Blight with is_reliable=False
        mgmt = get_disease_management('Tomato___Early_blight', is_reliable=False, is_compatible=True)
        self.assertTrue(mgmt['treatment_withheld'])
        self.assertEqual(len(mgmt['treatment_options']['chemical']), 0)
        self.assertIn('withheld', mgmt['withheld_reason'].lower())

    def test_treatment_withholding_on_species_incompatibility(self):
        """Ensure chemical treatments are strictly withheld when host species is incompatible."""
        mgmt = get_disease_management('Tomato___Early_blight', is_reliable=True, is_compatible=False)
        self.assertTrue(mgmt['treatment_withheld'])
        self.assertEqual(len(mgmt['treatment_options']['chemical']), 0)

    def test_disease_detection_api_returns_management_object(self):
        """Verify /api/disease-detection returns full structured management object."""
        # Create small test leaf image
        img = Image.new('RGB', (224, 224), color=(34, 139, 34))
        # Add random texture
        img_arr = np.array(img)
        img_arr += np.random.randint(0, 30, img_arr.shape, dtype=np.uint8)
        noisy_img = Image.fromarray(img_arr)
        buf = io.BytesIO()
        noisy_img.save(buf, format='JPEG')
        buf.seek(0)

        data = {
            'image': (buf, 'test_leaf.jpg')
        }
        res = self.client.post('/api/disease-detection',
                               data=data,
                               content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        res_data = res.get_json()
        self.assertTrue(res_data['success'])
        self.assertIn('management', res_data)
        mgmt = res_data['management']
        self.assertIn('pathogen_type', mgmt)
        self.assertIn('causal_agent', mgmt)
        self.assertIn('immediate_actions', mgmt)
        self.assertIn('treatment_options', mgmt)

    def test_disease_evaluation_api(self):
        """Verify /api/disease-evaluation serves real held-out MobileNetV2 metrics."""
        res = self.client.get('/api/disease-evaluation')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['num_classes'], 38)
        self.assertEqual(data['test_samples'], 731)
        self.assertEqual(data['metrics']['accuracy'], 96.72)
        self.assertIn('benchmark_notice', data)

    def test_benchmark_latency_api(self):
        """Verify /api/benchmark-latency measures real model execution latency."""
        res = self.client.get('/api/benchmark-latency')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('benchmarks', data)
        self.assertIn('crop_model', data['benchmarks'])
        self.assertIn('disease_model', data['benchmarks'])
        self.assertGreater(data['benchmarks']['crop_model']['mean_ms'], 0)
        self.assertGreater(data['benchmarks']['disease_model']['mean_ms'], 0)

if __name__ == '__main__':
    unittest.main()
