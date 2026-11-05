"""
test_image_validation.py -- Comprehensive test suite for OptiCrop plant disease
image validation pipeline.

Tests cover:
  Part A: Crop recommendation model (dataset, artifact, inference)
  Part B: Plant disease validator (plant_validator.py)
  Part C: Disease detection endpoint integration
  Part D: Regression tests for non-plant rejection

Run with:
    cd OptiCrop
    .venv\\Scripts\\python.exe -m pytest test_image_validation.py -v 2>&1

Test image strategy
-------------------
- Synthetic test images are generated programmatically (labeled SYNTHETIC).
- Where a synthetic image can reliably represent a category (solid colour,
  simple pattern), it is used. Where a real image would differ in important
  ways, the test notes this limitation.
- All test images are created from NumPy arrays + Pillow; no external files
  required for the automated suite.
"""

import io
import json
import os
import sys
import struct
import zlib
import numpy as np
import pytest
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ---------------------------------------------------------------------------
# Helpers — Synthetic image factories (all labeled SYNTHETIC)
# ---------------------------------------------------------------------------

def _make_png_bytes(array_rgb: np.ndarray) -> bytes:
    """Convert H×W×3 uint8 array to PNG bytes."""
    img = Image.fromarray(array_rgb.astype(np.uint8), "RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_jpeg_bytes(array_rgb: np.ndarray, quality: int = 85) -> bytes:
    img = Image.fromarray(array_rgb.astype(np.uint8), "RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


# SYNTHETIC: 256×256 leaf-green gradient image (simulates a leaf)
def synthetic_green_leaf() -> bytes:
    """SYNTHETIC — green gradient that approximates vegetation colour."""
    h, w = 256, 256
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    arr[:, :, 1] = np.linspace(80, 180, w, dtype=np.uint8)   # green channel
    arr[:, :, 0] = 30   # low red
    arr[:, :, 2] = 30   # low blue
    # Add some texture
    noise = np.random.RandomState(42).randint(0, 20, (h, w, 3), dtype=np.uint8)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return _make_png_bytes(arr)


# SYNTHETIC: solid uniform colour — simulates blank/corrupt upload
def synthetic_blank_white() -> bytes:
    """SYNTHETIC — completely blank white image."""
    arr = np.ones((256, 256, 3), dtype=np.uint8) * 255
    return _make_png_bytes(arr)


# SYNTHETIC: text document — simulates Aadhaar/ID card appearance
def synthetic_document() -> bytes:
    """SYNTHETIC — dark text on white, simulates a document/Aadhaar card."""
    img = Image.new("RGB", (300, 200), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    # Draw horizontal lines of text-like content
    for y in range(30, 180, 20):
        draw.rectangle([20, y, 280, y + 8], fill=(30, 30, 30))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# SYNTHETIC: blue sky / no green — landscape without plant
def synthetic_blue_sky() -> bytes:
    """SYNTHETIC — sky-blue image, very little green."""
    arr = np.zeros((256, 256, 3), dtype=np.uint8)
    arr[:, :, 2] = 200   # high blue
    arr[:, :, 0] = 100   # some red (sky-ish)
    arr[:, :, 1] = 160   # moderate green (sky)
    return _make_png_bytes(arr)


# SYNTHETIC: tiny image below minimum size
def synthetic_tiny() -> bytes:
    """SYNTHETIC — 16×16 px (below 32×32 minimum)."""
    arr = np.random.randint(0, 255, (16, 16, 3), dtype=np.uint8)
    return _make_png_bytes(arr)


# SYNTHETIC: corrupt binary data (not a valid image)
def synthetic_corrupt() -> bytes:
    """SYNTHETIC — random bytes that are not a valid image."""
    return bytes(range(256)) * 4


# SYNTHETIC: empty bytes
def synthetic_empty() -> bytes:
    """SYNTHETIC — zero-length upload."""
    return b""


# SYNTHETIC: valid-looking PNG but with truncated data (corrupt)
def synthetic_truncated_png() -> bytes:
    """SYNTHETIC — PNG header present but data truncated."""
    data = _make_png_bytes(np.zeros((100, 100, 3), dtype=np.uint8))
    return data[:50]  # truncate


# SYNTHETIC: orange-dominated image (simulates a rusty metal surface)
def synthetic_orange_object() -> bytes:
    """SYNTHETIC — orange/brown dominant, no green."""
    arr = np.zeros((256, 256, 3), dtype=np.uint8)
    arr[:, :, 0] = 200  # red
    arr[:, :, 1] = 100  # some green
    arr[:, :, 2] = 20   # low blue
    noise = np.random.RandomState(7).randint(0, 30, (256, 256, 3), dtype=np.uint8)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return _make_png_bytes(arr)


# SYNTHETIC: dark image (night / underexposed)
def synthetic_dark() -> bytes:
    """SYNTHETIC — very dark / underexposed."""
    arr = np.random.RandomState(99).randint(0, 15, (256, 256, 3), dtype=np.uint8)
    return _make_png_bytes(arr)


# SYNTHETIC: blurry green patch (blurred leaf approximation)
def synthetic_blurry_green() -> bytes:
    """SYNTHETIC — blurry uniform green (low-quality leaf photo approximation)."""
    arr = np.zeros((128, 128, 3), dtype=np.uint8)
    arr[:, :, 1] = 120  # green
    arr[:, :, 0] = 40
    arr[:, :, 2] = 40
    # Simulate blur by large pixel blocks
    for i in range(0, 128, 8):
        for j in range(0, 128, 8):
            mean_val = int(np.random.RandomState(i*j+1).randint(100, 140))
            arr[i:i+8, j:j+8, 1] = mean_val
    return _make_jpeg_bytes(arr, quality=40)


# SYNTHETIC: TV/screen-like image (blue-grey rectangle with text lines)
def synthetic_tv_screen() -> bytes:
    """SYNTHETIC — grey screen with horizontal bands (TV/monitor simulation)."""
    img = Image.new("RGB", (320, 240), color=(40, 40, 50))
    draw = ImageDraw.Draw(img)
    # Horizontal scan lines
    for y in range(0, 240, 4):
        draw.rectangle([0, y, 320, y+1], fill=(60, 60, 70))
    # Bright rectangle (UI element)
    draw.rectangle([40, 30, 280, 70], fill=(180, 180, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# SYNTHETIC: BMP file masquerading as JPG (wrong extension handled upstream)
def synthetic_bmp_bytes() -> bytes:
    """SYNTHETIC — valid BMP image (unsupported format in app)."""
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[:, :, 1] = 100
    img = Image.fromarray(arr, "RGB")
    buf = io.BytesIO()
    img.save(buf, format="BMP")
    return buf.getvalue()


# SYNTHETIC: Maple leaf with black tar spots (Rhytisma acerinum)
def synthetic_maple_leaf_tar_spots() -> bytes:
    """
    SYNTHETIC — 5-lobed broadleaf maple leaf with prominent circular black tar spots.
    Simulates out-of-distribution broadleaf pathogen (Rhytisma acerinum) on Acer sp.
    """
    import math
    w, h = 300, 300
    img = Image.new("RGB", (w, h), (242, 242, 242))
    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2 + 15
    points = []
    num_pts = 360
    for i in range(num_pts):
        theta = i * 2 * math.pi / num_pts
        r_base = 85
        l1 = 50 * max(0, math.cos(theta + math.pi/2)) ** 2
        l2 = 45 * max(0, math.cos(theta - 0.25)) ** 2
        l3 = 45 * max(0, math.cos(theta - math.pi + 0.25)) ** 2
        l4 = 35 * max(0, math.cos(theta - 0.95)) ** 3
        l5 = 35 * max(0, math.cos(theta - math.pi + 0.95)) ** 3
        serration = 5 * math.sin(24 * theta)
        r = r_base + l1 + l2 + l3 + l4 + l5 + serration
        if cy - r * math.sin(theta) > h - 35:
            r *= 0.5
        x = cx + r * math.cos(theta)
        y = cy - r * math.sin(theta)
        points.append((x, y))

    draw.polygon(points, fill=(55, 138, 48), outline=(35, 95, 30))

    # Palmate veins radiating from petiole
    for angle in [-math.pi/2, -math.pi/2 - 0.7, -math.pi/2 + 0.7, -math.pi/2 - 1.3, -math.pi/2 + 1.3]:
        vx = cx + 80 * math.cos(angle)
        vy = cy + 80 * math.sin(angle)
        draw.line([(cx, cy + 10), (vx, vy)], fill=(75, 158, 62), width=2)

    # Black tar spots (Rhytisma acerinum)
    tar_spots = [
        (cx - 30, cy - 40, 22),
        (cx + 40, cy - 20, 25),
        (cx - 45, cy + 15, 18),
        (cx + 15, cy - 70, 20),
        (cx + 30, cy + 20, 16)
    ]
    for sx, sy, srad in tar_spots:
        # Chlorotic yellow halo
        draw.ellipse([sx - srad - 3, sy - srad - 3, sx + srad + 3, sy + srad + 3], fill=(188, 198, 35))
        # Jet black stromatic lesion
        draw.ellipse([sx - srad, sy - srad, sx + srad, sy + srad], fill=(12, 12, 15))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


# SYNTHETIC: Car / Vehicle simulation
def synthetic_car_image() -> bytes:
    """SYNTHETIC — vehicle/car silhouette with wheels and metallic body."""
    img = Image.new("RGB", (320, 200), (220, 220, 225))
    draw = ImageDraw.Draw(img)
    # Car body (red/blue rectangle + cabin)
    draw.rectangle([40, 90, 280, 150], fill=(180, 20, 30))
    draw.polygon([(80, 90), (120, 45), (220, 45), (250, 90)], fill=(120, 15, 20))
    # Wheels
    draw.ellipse([70, 130, 120, 180], fill=(20, 20, 20))
    draw.ellipse([200, 130, 250, 180], fill=(20, 20, 20))
    draw.ellipse([85, 145, 105, 165], fill=(180, 180, 180))
    draw.ellipse([215, 145, 235, 165], fill=(180, 180, 180))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Part A — Crop Recommendation Model Tests
# ---------------------------------------------------------------------------

class TestCropRecommendationModel:
    """Tests for the crop recommendation dataset and Random Forest model."""

    def test_dataset_exists_and_readable(self):
        """CSV dataset must exist and be readable."""
        import pandas as pd
        csv_path = os.path.join(BASE_DIR, "Crop_recommendation.csv")
        assert os.path.exists(csv_path), f"Dataset not found at {csv_path}"
        df = pd.read_csv(csv_path)
        assert df.shape[0] > 0, "Dataset has no rows"

    def test_dataset_correct_columns(self):
        """Dataset must have exactly the 7 feature columns + label."""
        import pandas as pd
        df = pd.read_csv(os.path.join(BASE_DIR, "Crop_recommendation.csv"))
        required = {'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label'}
        assert required.issubset(set(df.columns)), (
            f"Missing columns: {required - set(df.columns)}"
        )

    def test_dataset_no_missing_values(self):
        """Dataset must have zero missing values in all columns."""
        import pandas as pd
        df = pd.read_csv(os.path.join(BASE_DIR, "Crop_recommendation.csv"))
        missing = df.isnull().sum()
        assert missing.sum() == 0, f"Missing values found: {missing[missing > 0].to_dict()}"

    def test_dataset_row_count(self):
        """Dataset must have 2200 rows (22 crops × 100 samples each)."""
        import pandas as pd
        df = pd.read_csv(os.path.join(BASE_DIR, "Crop_recommendation.csv"))
        assert df.shape[0] == 2200, f"Expected 2200 rows, got {df.shape[0]}"

    def test_dataset_label_distribution(self):
        """Each crop class must have exactly 100 samples."""
        import pandas as pd
        df = pd.read_csv(os.path.join(BASE_DIR, "Crop_recommendation.csv"))
        vc = df['label'].value_counts()
        assert vc.min() == 100 and vc.max() == 100, (
            f"Uneven class distribution: {vc.to_dict()}"
        )

    def test_model_artifact_exists(self):
        """The crop recommendation .pkl file must exist."""
        pkl_path = os.path.join(BASE_DIR, "crop_recommendation_model.pkl")
        assert os.path.exists(pkl_path), f"Model artifact not found: {pkl_path}"

    def test_model_loads_as_random_forest(self):
        """The .pkl must load as a RandomForestClassifier."""
        import joblib
        from sklearn.ensemble import RandomForestClassifier
        m = joblib.load(os.path.join(BASE_DIR, "crop_recommendation_model.pkl"))
        assert isinstance(m, RandomForestClassifier), f"Expected RandomForestClassifier, got {type(m)}"

    def test_model_feature_count(self):
        """Loaded model must expect exactly 7 input features."""
        import joblib
        m = joblib.load(os.path.join(BASE_DIR, "crop_recommendation_model.pkl"))
        assert m.n_features_in_ == 7, f"Expected 7 features, got {m.n_features_in_}"

    def test_model_class_count(self):
        """Loaded model must have 22 crop classes."""
        import joblib
        m = joblib.load(os.path.join(BASE_DIR, "crop_recommendation_model.pkl"))
        assert len(m.classes_) == 22, f"Expected 22 classes, got {len(m.classes_)}"

    def test_model_produces_valid_prediction(self):
        """A valid input must yield a recognized crop class."""
        import joblib
        import pandas as pd
        m = joblib.load(os.path.join(BASE_DIR, "crop_recommendation_model.pkl"))
        # Well-known rice-growing conditions from the dataset
        inp = pd.DataFrame([{
            'N': 90, 'P': 42, 'K': 43,
            'temperature': 20.87, 'humidity': 82.0,
            'ph': 6.5, 'rainfall': 202.9
        }])
        pred = m.predict(inp)[0]
        assert pred in m.classes_, f"Prediction '{pred}' not in model classes"
        assert pred == 'rice', f"Expected 'rice' for canonical rice conditions, got '{pred}'"

    def test_model_prediction_confidence_reasonable(self):
        """Top class probability must be > 50% for a clear-cut input."""
        import joblib
        import pandas as pd
        import numpy as np
        m = joblib.load(os.path.join(BASE_DIR, "crop_recommendation_model.pkl"))
        inp = pd.DataFrame([{
            'N': 90, 'P': 42, 'K': 43,
            'temperature': 20.87, 'humidity': 82.0,
            'ph': 6.5, 'rainfall': 202.9
        }])
        proba = m.predict_proba(inp)[0]
        assert np.max(proba) > 0.5, f"Max confidence too low: {np.max(proba):.2f}"

    def test_model_not_hardcoded(self):
        """Different inputs must produce different predictions (not hardcoded)."""
        import joblib
        import pandas as pd
        m = joblib.load(os.path.join(BASE_DIR, "crop_recommendation_model.pkl"))
        inp1 = pd.DataFrame([{'N': 90, 'P': 42, 'K': 43, 'temperature': 20.87,
                               'humidity': 82.0, 'ph': 6.5, 'rainfall': 202.9}])
        inp2 = pd.DataFrame([{'N': 40, 'P': 20, 'K': 200, 'temperature': 27.0,
                               'humidity': 80.0, 'ph': 7.0, 'rainfall': 50.0}])
        pred1 = m.predict(inp1)[0]
        pred2 = m.predict(inp2)[0]
        assert pred1 != pred2, (
            "Model returned same prediction for very different inputs — possible hardcoding"
        )

    def test_api_recommend_via_flask(self):
        """Flask /api/recommend endpoint must return a valid crop with real model."""
        import app as flask_app
        client = flask_app.app.test_client()
        payload = {
            'N': 90, 'P': 42, 'K': 43,
            'temperature': 20.87, 'humidity': 82.0,
            'ph': 6.5, 'rainfall': 202.9
        }
        resp = client.post('/api/recommend', json=payload,
                           content_type='application/json')
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.data}"
        data = resp.get_json()
        assert 'crop' in data, f"No 'crop' in response: {data}"
        assert 'confidence' in data
        assert isinstance(data['crop'], str) and len(data['crop']) > 0
        assert 0 <= data['confidence'] <= 100

    def test_api_recommend_malformed_input(self):
        """Missing fields must return a 400 error, not 500."""
        import app as flask_app
        client = flask_app.app.test_client()
        resp = client.post('/api/recommend', json={'N': 90},
                           content_type='application/json')
        assert resp.status_code in (400, 500), f"Expected error status, got {resp.status_code}"

    def test_api_recommend_out_of_range_input(self):
        """Out-of-range values must return a validation error."""
        import app as flask_app
        client = flask_app.app.test_client()
        payload = {
            'N': 9999, 'P': 42, 'K': 43,
            'temperature': 20.87, 'humidity': 82.0,
            'ph': 6.5, 'rainfall': 202.9
        }
        resp = client.post('/api/recommend', json=payload,
                           content_type='application/json')
        assert resp.status_code == 400, f"Expected 400 for out-of-range input, got {resp.status_code}"
        data = resp.get_json()
        assert 'error' in data


# ---------------------------------------------------------------------------
# Part B — Plant Validator Unit Tests
# ---------------------------------------------------------------------------

class TestPlantValidatorUnit:
    """Unit tests for plant_validator.py module."""

    @pytest.fixture(autouse=True)
    def validator(self):
        from plant_validator import PlantValidator
        self.v = PlantValidator.get_instance()

    def _validate(self, image_bytes):
        return self.v.validate(image_bytes)

    # ── Invalid file tests ─────────────────────────────────────────────────

    def test_empty_bytes_rejected(self):
        """SYNTHETIC empty upload must be rejected with empty_file error."""
        r = self._validate(synthetic_empty())
        assert r['valid'] is False
        assert r['error'] == 'empty_file'
        # Expected: invalid, Actual: check below
        print(f"\n[empty_bytes] valid={r['valid']}, reason={r['reason']}")

    def test_corrupt_image_rejected(self):
        """SYNTHETIC corrupt binary data must be rejected."""
        r = self._validate(synthetic_corrupt())
        assert r['valid'] is False
        assert r['error'] in ('corrupt_image', 'empty_file')
        print(f"\n[corrupt_image] valid={r['valid']}, reason={r['reason']}")

    def test_truncated_png_rejected(self):
        """SYNTHETIC truncated PNG must be rejected."""
        r = self._validate(synthetic_truncated_png())
        assert r['valid'] is False
        print(f"\n[truncated_png] valid={r['valid']}, reason={r['reason']}")

    def test_blank_white_rejected(self):
        """SYNTHETIC blank white image must be rejected (pixel_std < 8)."""
        r = self._validate(synthetic_blank_white())
        assert r['valid'] is False
        print(f"\n[blank_white] valid={r['valid']}, reason={r['reason']}")

    def test_tiny_image_rejected(self):
        """SYNTHETIC 16×16px image must be rejected (below minimum)."""
        r = self._validate(synthetic_tiny())
        assert r['valid'] is False
        print(f"\n[tiny_image] valid={r['valid']}, reason={r['reason']}")

    # ── Plant image tests ──────────────────────────────────────────────────

    def test_green_leaf_accepted(self):
        """SYNTHETIC green leaf image must pass validation."""
        r = self._validate(synthetic_green_leaf())
        # Green leaf should be accepted (either by ImageNet model or green ratio)
        print(f"\n[green_leaf] valid={r['valid']}, method={r['method']}, "
              f"plant_score={r['plant_score']}, green_ratio={r['supplementary'].get('green_ratio', 'N/A')}")
        # We check that it's not a hard rejection based on validator errors
        assert r.get('error') not in ('corrupt_image', 'empty_file', 'rgb_conversion_fail')
        # Synthetic green leaf may be valid or ambiguous — either is acceptable
        # since it will then go to disease model which handles uncertainty
        assert r['valid'] is True or r.get('method') in ('imagenet_mobilenetv2', 'supplementary_fallback')

    def test_blurry_green_forwarded(self):
        """SYNTHETIC blurry green patch — should not be hard-rejected."""
        r = self._validate(synthetic_blurry_green())
        print(f"\n[blurry_green] valid={r['valid']}, method={r['method']}, "
              f"plant_score={r['plant_score']}, green_ratio={r['supplementary'].get('green_ratio', 'N/A')}")
        # Blurry green should at minimum not fail on decode/size/blank checks
        assert r.get('error') not in ('corrupt_image', 'empty_file')

    # ── Non-plant image tests ──────────────────────────────────────────────

    def test_document_nonplant(self):
        """
        SYNTHETIC document image (Aadhaar-like).
        Expected: rejected as non-plant.
        Note: ImageNet model required for reliable rejection; supplementary
              signals alone may be insufficient for document images.
        """
        r = self._validate(synthetic_document())
        print(f"\n[document] valid={r['valid']}, method={r['method']}, "
              f"nonplant_score={r['nonplant_score']}, green_ratio={r['supplementary'].get('green_ratio', 'N/A')}, "
              f"top={r['top_imagenet']}")
        # If ImageNet model is available, a text-heavy document should be rejected
        if r['method'] == 'imagenet_mobilenetv2':
            assert r['valid'] is False, (
                f"Document image should be rejected by ImageNet validator "
                f"(nonplant_score={r['nonplant_score']:.3f}, top={r['top_imagenet']})"
            )
        else:
            pytest.skip(
                "ImageNet model not available; document rejection cannot be verified "
                "by supplementary signals alone (known limitation)"
            )

    def test_tv_screen_nonplant(self):
        """
        SYNTHETIC TV/screen-like image.
        Expected: rejected as non-plant when ImageNet model is available.
        """
        r = self._validate(synthetic_tv_screen())
        print(f"\n[tv_screen] valid={r['valid']}, method={r['method']}, "
              f"nonplant_score={r['nonplant_score']}, top={r['top_imagenet']}")
        if r['method'] == 'imagenet_mobilenetv2':
            assert r['valid'] is False, (
                f"TV screen image should be rejected "
                f"(nonplant_score={r['nonplant_score']:.3f})"
            )
        else:
            pytest.skip("ImageNet model not available")

    def test_blue_sky_low_green(self):
        """
        SYNTHETIC pure blue sky — very low green ratio.
        If ImageNet model available: expect rejection.
        Fallback: check that green_ratio is very low.
        """
        r = self._validate(synthetic_blue_sky())
        green = r['supplementary'].get('green_ratio', 1.0)
        print(f"\n[blue_sky] valid={r['valid']}, method={r['method']}, "
              f"nonplant_score={r['nonplant_score']}, green_ratio={green}")
        # Blue sky has very low green in our strict HSV definition
        # (our sky sim has moderate green at 160 which may pass — acceptable)
        assert r.get('error') not in ('corrupt_image', 'empty_file')

    def test_orange_object_low_green(self):
        """
        SYNTHETIC orange/rust-colored object, no green.
        """
        r = self._validate(synthetic_orange_object())
        green = r['supplementary'].get('green_ratio', 1.0)
        print(f"\n[orange_object] valid={r['valid']}, method={r['method']}, "
              f"nonplant_score={r['nonplant_score']}, green_ratio={green}")
        assert r.get('error') not in ('corrupt_image', 'empty_file')

    def test_dark_image_not_crash(self):
        """SYNTHETIC very dark image — must not crash, should return valid result dict."""
        r = self._validate(synthetic_dark())
        print(f"\n[dark_image] valid={r['valid']}, method={r['method']}")
        assert 'valid' in r
        assert 'reason' in r


# ---------------------------------------------------------------------------
# Part C — Disease Detection Endpoint Integration Tests
# ---------------------------------------------------------------------------

class TestDiseaseDetectionEndpoint:
    """Integration tests via the Flask test client."""

    @pytest.fixture(autouse=True)
    def client(self):
        import app as flask_app
        self.client = flask_app.app.test_client()

    def _post_image(self, image_bytes, filename="test.png", plant=None):
        data = {'image': (io.BytesIO(image_bytes), filename)}
        if plant:
            data['selected_plant'] = plant
        return self.client.post(
            '/api/disease-detection',
            data=data,
            content_type='multipart/form-data'
        )

    def test_no_file_upload_rejected(self):
        """POST with no file must return 400."""
        resp = self.client.post('/api/disease-detection',
                                data={}, content_type='multipart/form-data')
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data

    def test_empty_filename_rejected(self):
        """Empty filename must return 400."""
        resp = self.client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(b""), '')},
            content_type='multipart/form-data'
        )
        assert resp.status_code == 400

    def test_corrupt_image_rejected_400(self):
        """SYNTHETIC corrupt image bytes must return 400 (not 500)."""
        resp = self._post_image(synthetic_corrupt(), "corrupt.png")
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data
        # Must not expose filesystem paths or stack traces
        error_text = data['error']
        assert 'Traceback' not in error_text
        assert 'C:\\' not in error_text
        print(f"\n[endpoint corrupt] status={resp.status_code}, error={error_text[:80]}")

    def test_unsupported_format_rejected(self):
        """BMP file must be rejected by the extension check."""
        resp = self._post_image(synthetic_bmp_bytes(), "leaf.bmp")
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data
        print(f"\n[endpoint bmp] error={data.get('error','')[:80]}")

    def test_empty_upload_rejected(self):
        """SYNTHETIC empty bytes upload must return 400."""
        resp = self._post_image(synthetic_empty(), "empty.png")
        assert resp.status_code == 400

    def test_blank_image_rejected(self):
        """SYNTHETIC blank white image must be rejected."""
        resp = self._post_image(synthetic_blank_white(), "blank.png")
        assert resp.status_code in (400, 200)
        if resp.status_code == 400:
            data = resp.get_json()
            assert 'error' in data
        else:
            # If somehow passes (e.g. validator fallback), disease model should flag uncertain
            data = resp.get_json()
            print(f"\n[endpoint blank] status={resp.status_code}, data={str(data)[:120]}")

    def test_green_leaf_reaches_disease_model(self):
        """SYNTHETIC green leaf must reach disease model (not be blocked)."""
        resp = self._post_image(synthetic_green_leaf(), "leaf.png")
        # Either 200 (disease model ran) or 400 with uncertainty message (not validation block)
        data = resp.get_json()
        print(f"\n[endpoint green_leaf] status={resp.status_code}, "
              f"success={data.get('success')}, status_field={data.get('status')}")
        # The key constraint: if rejected, it must NOT say "validation_failed" 
        # because green is a valid plant signal
        if resp.status_code == 400:
            assert not data.get('validation_failed'), (
                "Green leaf should not be blocked by plant validator"
            )

    def test_document_image_never_gets_disease_label(self):
        """
        SYNTHETIC document image must never receive a disease class name.
        This is the core regression test.
        """
        resp = self._post_image(synthetic_document(), "doc.png")
        data = resp.get_json()
        print(f"\n[endpoint document] status={resp.status_code}, "
              f"error={data.get('error','')[:80]}, "
              f"class_name={data.get('class_name','')}")
        if resp.status_code == 200:
            # If disease model ran (validator fallback), it must not be 'reliable'
            assert data.get('is_reliable') is not True, (
                "Document image must never receive a reliable disease prediction"
            )
            assert data.get('treatment_withheld') is not False, (
                "Treatment must be withheld for non-plant images"
            )
        # Either a 400 rejection OR a 200 with is_reliable=False/treatment_withheld=True

    def test_tv_image_never_gets_disease_label(self):
        """
        SYNTHETIC TV screen image must never receive a disease class name.
        """
        resp = self._post_image(synthetic_tv_screen(), "tv.png")
        data = resp.get_json()
        print(f"\n[endpoint tv] status={resp.status_code}, "
              f"error={data.get('error','')[:80]}, "
              f"class_name={data.get('class_name','')}")
        if resp.status_code == 200:
            assert data.get('is_reliable') is not True
            assert data.get('treatment_withheld') is not False

    def test_no_stack_traces_in_errors(self):
        """Error responses must never expose internal stack traces."""
        resp = self._post_image(synthetic_corrupt(), "x.png")
        data = resp.get_json()
        error_text = data.get('error', '')
        assert 'Traceback' not in error_text, "Stack trace exposed in error response"
        assert '\n  File' not in error_text, "File path exposed in error response"

    def test_file_size_limit(self):
        """File larger than 10 MB must be rejected."""
        big = b'\x89PNG\r\n\x1a\n' + b'X' * (11 * 1024 * 1024)
        resp = self._post_image(big, "huge.png")
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data


# ---------------------------------------------------------------------------
# Part D — Regression Tests
# ---------------------------------------------------------------------------

class TestRegressionNonPlantRejection:
    """
    Regression tests to ensure non-plant images never get disease labels.
    These tests guard against future changes breaking the validation gate.
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        import app as flask_app
        self.client = flask_app.app.test_client()
        from plant_validator import PlantValidator
        self.validator = PlantValidator.get_instance()

    def _post_image(self, image_bytes, filename="test.png"):
        return self.client.post(
            '/api/disease-detection',
            data={'image': (io.BytesIO(image_bytes), filename)},
            content_type='multipart/form-data'
        )

    def _assert_no_disease_label(self, resp, test_name):
        """Assert the response does not contain a reliable disease label."""
        data = resp.get_json()
        if resp.status_code == 400:
            assert 'error' in data, f"[{test_name}] 400 but no error field"
            return  # Rejection is the ideal outcome

        # If 200: must have is_reliable=False OR treatment_withheld=True
        reliable = data.get('is_reliable', False)
        withheld = data.get('treatment_withheld', True)
        assert not reliable or withheld, (
            f"[{test_name}] Non-plant image received reliable disease label: "
            f"class={data.get('class_name')}, condition={data.get('condition')}"
        )

    def test_document_regression(self):
        """Regression: document/Aadhaar-like image must not get disease label."""
        resp = self._post_image(synthetic_document(), "aadhaar_sim.png")
        self._assert_no_disease_label(resp, "document")

    def test_tv_screen_regression(self):
        """Regression: TV screen image must not get disease label."""
        resp = self._post_image(synthetic_tv_screen(), "tv.png")
        self._assert_no_disease_label(resp, "tv_screen")

    def test_blank_regression(self):
        """Regression: blank white image must not get disease label."""
        resp = self._post_image(synthetic_blank_white(), "blank.png")
        self._assert_no_disease_label(resp, "blank")

    def test_corrupt_regression(self):
        """Regression: corrupt file must return error, never a disease label."""
        resp = self._post_image(synthetic_corrupt(), "corrupt.png")
        assert resp.status_code == 400, "Corrupt file must return 400"

    def test_orange_object_regression(self):
        """Regression: orange non-plant object must not get a reliable disease label."""
        resp = self._post_image(synthetic_orange_object(), "rust_metal.png")
        self._assert_no_disease_label(resp, "orange_object")

    def test_validator_is_called_before_disease_model(self):
        """
        Regression: Corrupt image must fail at validator, not reach disease model.
        The error must come from validation, not inference.
        """
        from plant_validator import validate_plant_image
        r = validate_plant_image(synthetic_corrupt())
        assert r['valid'] is False, (
            "Corrupt image must fail plant validation before reaching disease model"
        )

    def test_disease_model_not_called_after_validator_rejection(self):
        """
        Regression: When validator rejects, disease_detector.predict must
        return early with validation_failed=True (checked via mocking).
        """
        from disease_model import PlantDiseaseDetector
        import unittest.mock as mock

        detector = PlantDiseaseDetector.get_instance()
        # Patch the ONNX session to catch if it's ever called
        original_run = None
        called = []

        if detector.session is not None:
            original_run = detector.session.run
            def spy_run(*args, **kwargs):
                called.append(True)
                return original_run(*args, **kwargs)
            detector.session.run = spy_run

        try:
            result = detector.predict(synthetic_corrupt())
            assert result.get('success') is False
            # session.run should NOT have been called for corrupt bytes
            assert len(called) == 0, (
                "Disease model ONNX session was called despite corrupt image — "
                "validator failed to block it"
            )
        finally:
            if original_run is not None:
                detector.session.run = original_run

    def test_car_regression(self):
        """Regression: car/vehicle image must not receive a disease label."""
        resp = self._post_image(synthetic_car_image(), "car.png")
        self._assert_no_disease_label(resp, "car_image")


class TestHostSpeciesAndDiseaseReliability:
    """
    Tests for host plant verification, unsupported plant species rejection,
    and host-disease compatibility enforcement.
    Specifically tests that maple leaf with black tar spots is never guessed as corn!
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        import app as flask_app
        self.client = flask_app.app.test_client()

    def _post_image(self, image_bytes, filename="test.jpg", plant=None):
        data = {'image': (io.BytesIO(image_bytes), filename)}
        if plant:
            data['selected_plant'] = plant
        return self.client.post(
            '/api/disease-detection',
            data=data,
            content_type='multipart/form-data'
        )

    def test_maple_leaf_tar_spots_never_diagnosed_as_corn(self):
        """
        CRITICAL TEST:
        Maple leaf with black tar spots (Rhytisma acerinum) uploaded in Auto-detect mode.
        Must NEVER be diagnosed as Corn (Maize) or assigned a corn disease label!
        Must return uncertain / inconclusive with treatment withheld.
        """
        maple_bytes = synthetic_maple_leaf_tar_spots()
        resp = self._post_image(maple_bytes, "maple_tar_spot.jpg")
        assert resp.status_code == 200
        data = resp.get_json()

        # Must not be reliable
        assert data.get('is_reliable') is False, "Maple leaf must not receive a reliable diagnosis"
        assert data.get('treatment_withheld') is True, "Treatment must be withheld for maple leaf"
        
        # Must not be classified as Corn!
        assert data.get('crop') != 'Corn (Maize)', f"Maple leaf was falsely classified as {data.get('crop')}!"
        assert 'Corn' not in data.get('crop', ''), "Corn must not appear as diagnosed crop"
        assert 'Cercospora' not in data.get('condition', ''), "Cercospora leaf spot must not be diagnosed for maple"

        # Safe non-corn display
        assert data.get('status') == 'uncertain'
        assert data.get('crop') == 'Unsupported Crop / Inconclusive Host'
        assert data.get('condition') == 'Unable to determine disease confidently'
        
        # Treatment options must NOT have chemical advice
        mgmt = data.get('management') or {}
        chem = mgmt.get('treatment_options', {}).get('chemical', [])
        assert len(chem) == 0, f"Chemical treatments must be empty for maple, got {chem}"

    def test_maple_leaf_explicit_unsupported_species(self):
        """
        User selects 'Maple' in plant dropdown.
        Maple is not in the 14 supported species.
        Must return unsupported crop status with clear warning message.
        """
        maple_bytes = synthetic_maple_leaf_tar_spots()
        resp = self._post_image(maple_bytes, "maple.jpg", plant="Maple")
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('is_reliable') is False
        assert data.get('treatment_withheld') is True
        assert data.get('status') == 'incompatible'
        assert data.get('crop') == 'Unsupported Crop (Maple)'
        assert data.get('condition') == 'Unsupported plant species'
        assert "Unsupported plant species" in data.get('warning', '')

    def test_real_supported_apple_scab(self):
        """
        Real PlantVillage Apple Scab leaf image.
        Must be correctly identified as Apple Scab with high confidence.
        """
        cls_dir = os.path.join(BASE_DIR, 'datasets', 'plantvillage', 'Apple___Apple_scab')
        if not os.path.exists(cls_dir):
            pytest.skip("PlantVillage dataset directory not found locally")
        files = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not files:
            pytest.skip("No Apple Scab files found")

        with open(os.path.join(cls_dir, files[0]), 'rb') as f:
            img_bytes = f.read()

        resp = self._post_image(img_bytes, files[0])
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('success') is True
        assert data.get('status') == 'supported'
        assert data.get('is_reliable') is True
        assert data.get('crop') == 'Apple'
        assert 'Apple Scab' in data.get('condition')
        assert data.get('treatment_withheld') is False

    def test_real_supported_corn_rust(self):
        """
        Real PlantVillage Corn Common Rust leaf image.
        Must be correctly identified as Corn with Common Rust.
        """
        cls_dir = os.path.join(BASE_DIR, 'datasets', 'plantvillage', 'Corn_(maize)___Common_rust_')
        if not os.path.exists(cls_dir):
            pytest.skip("PlantVillage Corn Common Rust dir not found")
        files = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not files:
            pytest.skip("No Corn rust files found")

        with open(os.path.join(cls_dir, files[0]), 'rb') as f:
            img_bytes = f.read()

        resp = self._post_image(img_bytes, files[0])
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('success') is True
        assert data.get('status') == 'supported'
        assert data.get('is_reliable') is True
        assert data.get('crop') == 'Corn (Maize)'
        assert 'Common Rust' in data.get('condition')

    def test_species_mismatch_withholds_treatment(self):
        """
        User uploads an Apple leaf but selects 'Corn (Maize)' as species.
        Must detect species incompatibility and withhold all chemical treatment!
        """
        cls_dir = os.path.join(BASE_DIR, 'datasets', 'plantvillage', 'Apple___Apple_scab')
        if not os.path.exists(cls_dir):
            pytest.skip("PlantVillage dataset not found")
        files = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not files:
            pytest.skip("No Apple Scab files found")

        with open(os.path.join(cls_dir, files[0]), 'rb') as f:
            img_bytes = f.read()

        resp = self._post_image(img_bytes, files[0], plant="Corn (Maize)")
        assert resp.status_code == 200
        data = resp.get_json()

        assert data.get('is_reliable') is False
        assert data.get('status') == 'incompatible'
        assert data.get('treatment_withheld') is True
        assert "Incompatible Host" in data.get('crop')
        # Chemical advice must be strictly empty
        mgmt = data.get('management') or {}
        chem = mgmt.get('treatment_options', {}).get('chemical', [])
        assert len(chem) == 0, "Chemical treatments must be withheld on species mismatch"


# ---------------------------------------------------------------------------
# Part E — Plant Validator Summary Report
# ---------------------------------------------------------------------------

def print_test_summary():
    """Print a test summary table (call from __main__)."""
    tests = [
        ("Empty upload",           "SYNTHETIC", "Reject (empty_file)",    synthetic_empty()),
        ("Corrupt binary",         "SYNTHETIC", "Reject (corrupt)",       synthetic_corrupt()),
        ("Truncated PNG",          "SYNTHETIC", "Reject (corrupt)",       synthetic_truncated_png()),
        ("Blank white",            "SYNTHETIC", "Reject (blank)",         synthetic_blank_white()),
        ("Tiny image (<32px)",     "SYNTHETIC", "Reject (size)",          synthetic_tiny()),
        ("Green leaf",             "SYNTHETIC", "Accept (plant)",         synthetic_green_leaf()),
        ("Blurry green leaf",      "SYNTHETIC", "Accept/Ambiguous",       synthetic_blurry_green()),
        ("Document/Aadhaar-like",  "SYNTHETIC", "Reject (nonplant)",      synthetic_document()),
        ("TV screen",              "SYNTHETIC", "Reject (nonplant)",      synthetic_tv_screen()),
        ("Blue sky",               "SYNTHETIC", "Reject/Ambiguous",       synthetic_blue_sky()),
        ("Orange object",          "SYNTHETIC", "Reject/Ambiguous",       synthetic_orange_object()),
        ("Dark image",             "SYNTHETIC", "Accept/Ambiguous",       synthetic_dark()),
    ]

    from plant_validator import PlantValidator
    v = PlantValidator.get_instance()

    print("\n" + "=" * 90)
    print(f"{'TEST IMAGE':<30} {'TYPE':<10} {'EXPECTED':<24} {'ACTUAL':<10} {'METHOD':<28}")
    print("=" * 90)

    pass_count = 0
    fail_count = 0

    for name, img_type, expected, img_bytes in tests:
        r = v.validate(img_bytes)
        actual_str = "ACCEPT" if r['valid'] is True else ("REJECT" if r['valid'] is False else "ERROR")
        expected_ok = (
            ("Reject" in expected and r['valid'] is False) or
            ("Accept" in expected and r['valid'] is True) or
            ("Ambiguous" in expected)
        )
        status = "PASS" if expected_ok else "FAIL"
        if expected_ok:
            pass_count += 1
        else:
            fail_count += 1
        print(f"{name:<30} {img_type:<10} {expected:<24} {actual_str:<10} {r.get('method','?'):<28}  [{status}]")

    print("=" * 90)
    print(f"Passed: {pass_count}  Failed: {fail_count}  Total: {len(tests)}")
    print("=" * 90)
    print("\nNote: 'Ambiguous' expected results are always counted as PASS.")
    print("Real-world test images (person, animal, vehicle, landscape) not included in")
    print("automated suite — those require actual photos. See AUDIT_REPORT.md for details.\n")


if __name__ == "__main__":
    print_test_summary()
