"""Test disease detection feature end-to-end."""
from app import app
client = app.test_client()

# Test 1: Disease page renders
res = client.get('/disease-detection')
print('=== Test 1: Disease page render ===')
print('Status:', res.status_code)
html = res.data.decode()
ids_to_check = ['disease-dropzone', 'disease-file-input', 'browse-files-btn', 
                'disease-preview-container', 'disease-preview-img', 'preview-filename',
                'preview-filesize', 'remove-image-btn', 'btn-analyze-disease',
                'disease-results-card', 'disease-result-crop', 'disease-result-condition',
                'disease-result-confidence', 'disease-confidence-fill', 'disease-severity-badge',
                'disease-caution-box', 'disease-caution-text', 'disease-symptoms',
                'disease-care-list', 'disease-prevention', 'top-candidates-container',
                'btn-open-catalog', 'disease-catalog-modal', 'btn-close-catalog', 'catalog-grid']
missing = [id for id in ids_to_check if ('id="' + id + '"') not in html]
if missing:
    print('MISSING IDs:', missing)
else:
    print('ALL 25 critical IDs present in HTML!')

# Test 2: Disease detection API
import io
from PIL import Image
img = Image.new('RGB', (224,224), (120, 80, 40))
buf = io.BytesIO()
img.save(buf, 'JPEG')
buf.seek(0)
res = client.post('/api/disease-detection', data={'image': (buf, 'test_leaf.jpg')}, content_type='multipart/form-data')
print()
print('=== Test 2: Disease detection API ===')
print('Status:', res.status_code)
data = res.get_json()
print('Success:', data.get('success'))
print('Crop:', data.get('crop'))
print('Condition:', data.get('condition'))
print('Confidence:', data.get('confidence'))
print('Severity:', data.get('severity'))
print('Has symptoms:', bool(data.get('symptoms')))
print('Has care_recs:', bool(data.get('care_recommendations')))
print('Has prevention:', bool(data.get('prevention')))
print('Top candidates count:', len(data.get('top_candidates', [])))

# Test 3: Disease classes API
res = client.get('/api/disease-classes')
print()
print('=== Test 3: Disease classes API ===')
print('Status:', res.status_code)
data = res.get_json()
print('Classes count:', len(data.get('classes', [])))

# Test 4: Health endpoint
res = client.get('/api/health')
print()
print('=== Test 4: Health endpoint ===')
print('Status:', res.status_code)
data = res.get_json()
print('Disease model loaded:', data.get('models', {}).get('plant_disease_model', {}).get('loaded'))

print()
print('=== ALL TESTS COMPLETE ===')
