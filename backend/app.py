import os
import json
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..")) if os.path.basename(BASE_DIR) == "backend" else BASE_DIR

for p in [
    BASE_DIR,
    os.path.join(BASE_DIR, "utils"),
    os.path.join(BASE_DIR, "models"),
    os.path.join(BASE_DIR, "config"),
    PROJECT_ROOT
]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

# Avoid watchdog reloader deadlock during vercel dev on Windows
if os.environ.get("VERCEL_DEV_FRAMEWORK") == "flask":
    try:
        import sys
        if "vercel_runtime.dev" in sys.modules:
            vr_dev = sys.modules["vercel_runtime.dev"]
            _orig_run = vr_dev.run_simple
            vr_dev.run_simple = lambda *a, **kw: _orig_run(*a, **{**kw, "use_reloader": False})
        import vercel_runtime._vendor.werkzeug.serving as vr_serving
        _orig_vr_run = vr_serving.run_simple
        vr_serving.run_simple = lambda *a, **kw: _orig_vr_run(*a, **{**kw, "use_reloader": False})
    except Exception:
        pass

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates") if os.path.exists(os.path.join(FRONTEND_DIR, "templates")) else os.path.join(PROJECT_ROOT, "templates")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static") if os.path.exists(os.path.join(FRONTEND_DIR, "static")) else (
    os.path.join(PROJECT_ROOT, "public", "static") if os.path.exists(os.path.join(PROJECT_ROOT, "public", "static")) else os.path.join(PROJECT_ROOT, "static")
)

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR,
    static_url_path="/static"
)

def _resolve_resource_path(*candidates):
    for c in candidates:
        if os.path.isabs(c) and os.path.exists(c):
            return c
        for base in [BASE_DIR, PROJECT_ROOT]:
            full = os.path.join(base, c)
            if os.path.exists(full):
                return full
    return os.path.join(BASE_DIR, candidates[0])

MODEL_PATH = _resolve_resource_path(os.path.join("models", "crop_recommendation_model.pkl"), "crop_recommendation_model.pkl")
STATS_PATH = _resolve_resource_path(os.path.join("config", "crop_stats.json"), "crop_stats.json")
DATA_PATH = _resolve_resource_path(os.path.join("datasets", "Crop_recommendation.csv"), os.path.join("config", "Crop_recommendation.csv"), "Crop_recommendation.csv")
EVAL_PATH = _resolve_resource_path(os.path.join("config", "evaluation_metrics.json"), "evaluation_metrics.json")

# Global variables for models and stats
model = None
crop_stats = None
disease_detector = None


def load_resources():
    global model, crop_stats, disease_detector
    print(f"Loading resources from: {MODEL_PATH} and {STATS_PATH}")
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("Crop recommendation model loaded successfully.")
    else:
        print("Model file NOT found!")
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH, 'r') as f:
            crop_stats = json.load(f)
        print("Crop stats loaded successfully.")
    else:
        print("Crop stats file NOT found!")
        
    try:
        from disease_model import PlantDiseaseDetector
        disease_detector = PlantDiseaseDetector.get_instance()
    except Exception as e:
        print(f"Disease detector startup notice: {e}")
    
    # Pre-load the plant validator so it's ready on first request
    try:
        from plant_validator import PlantValidator
        PlantValidator.get_instance()
    except Exception as e:
        print(f"Plant validator startup notice: {e}")

# Call load_resources immediately on import (for serverless environments like Vercel)
load_resources()

def validate_crop_inputs(values):
    limits = {
        "N": (0, 150),
        "P": (5, 150),
        "K": (5, 210),
        "temperature": (5, 50),
        "humidity": (10, 100),
        "ph": (3.5, 10),
        "rainfall": (10, 350),
    }

    for field, (minimum, maximum) in limits.items():
        value = values[field]

        if not np.isfinite(value):
            return f"{field} must be a valid finite number."

        if not minimum <= value <= maximum:
            return (
                f"{field} must be between "
                f"{minimum} and {maximum}."
            )

    return None

# Helper: calculate compatibility score and get recommendations
def calculate_suitability(crop_name, n, p, k, temp, hum, ph, rain):
    if not crop_stats or crop_name not in crop_stats:
        return None
    
    stats = crop_stats[crop_name]
    inputs = {
        'N': n,
        'P': p,
        'K': k,
        'temperature': temp,
        'humidity': hum,
        'ph': ph,
        'rainfall': rain
    }
    
    details = {}
    total_score = 0.0
    
    # Advice templates
    advice_templates = {
        'N': {
            'low': "Nitrogen level is insufficient. Apply Nitrogen-rich organic matter or chemical fertilizers like urea to enrich the soil.",
            'high': "Nitrogen is too high. Avoid adding nitrogenous fertilizers and grow heavy-feeding leafy greens or use cover crops to absorb excess nitrogen.",
            'optimal': "Nitrogen level is optimal for this crop."
        },
        'P': {
            'low': "Phosphorus is deficient. Apply bone meal, rock phosphate, or phosphate-rich fertilizers to promote healthy root development.",
            'high': "Phosphorus is excessive. High phosphorus can inhibit the absorption of other nutrients. Avoid adding phosphorus fertilizers.",
            'optimal': "Phosphorus level is optimal for this crop."
        },
        'K': {
            'low': "Potassium is low. Apply potash, compost, or wood ash to enhance crop disease resistance and overall quality.",
            'high': "Potassium is too high. This can interfere with magnesium and calcium absorption. Flush soil if possible and avoid potash.",
            'optimal': "Potassium level is optimal for this crop."
        },
        'temperature': {
            'low': "Temperature is too cold for this crop. Consider using green-houses, row covers, or planting in a warmer season.",
            'high': "Temperature is too hot. Provide shading structures, use mulching to keep roots cool, and irrigate during cooler morning hours.",
            'optimal': "Temperature is optimal for this crop."
        },
        'humidity': {
            'low': "Humidity is too low. Increase local humidity via misting systems, drip irrigation, or windbreaks.",
            'high': "Humidity is too high. Ensure proper spacing between crops to allow airflow, prune dense leaves, and avoid overhead watering to prevent fungal diseases.",
            'optimal': "Humidity is optimal for this crop."
        },
        'ph': {
            'low': "Soil is too acidic. Apply agricultural lime (calcium carbonate) or dolomite to raise the pH.",
            'high': "Soil is too alkaline. Apply sulfur, organic compost, or ammonium sulfate to lower the pH.",
            'optimal': "Soil pH is optimal for this crop."
        },
        'rainfall': {
            'low': "Rainfall is inadequate. Set up drip irrigation or sprinkler systems to supply supplementary watering.",
            'high': "Rainfall is excessive. Ensure robust drainage channels and raised beds to prevent root rot and waterlogging.",
            'optimal': "Rainfall is optimal for this crop."
        }
    }
    
    for feat, val in inputs.items():
        feat_stats = stats[feat]
        min_v = feat_stats['min']
        max_v = feat_stats['max']
        p10 = feat_stats['p10']
        p90 = feat_stats['p90']
        mean = feat_stats['mean']
        
        # Calculate individual suitability score
        # 1.0 if within p10 - p90
        # decays to 0.0 outside min - max
        if p10 <= val <= p90:
            score = 1.0
            status = "Optimal"
            status_color = "success"
            advice = advice_templates[feat]['optimal']
        elif val < p10:
            status = "Low" if val >= min_v else "Critically Low"
            status_color = "warning" if val >= min_v else "danger"
            advice = advice_templates[feat]['low']
            if p10 > min_v:
                score = max(0.0, (val - min_v) / (p10 - min_v))
            else:
                score = 0.0
        else:
            status = "High" if val <= max_v else "Critically High"
            status_color = "warning" if val <= max_v else "danger"
            advice = advice_templates[feat]['high']
            if max_v > p90:
                score = max(0.0, (max_v - val) / (max_v - p90))
            else:
                score = 0.0
                
        total_score += score
        details[feat] = {
            'current': round(val, 2),
            'optimal_range': f"{round(p10, 1)} - {round(p90, 1)}",
            'mean': round(mean, 2),
            'status': status,
            'status_color': status_color,
            'score': round(score * 100, 1),
            'remediation': advice
        }
        
    overall_score = round((total_score / len(inputs)) * 100, 1)
    
    return {
        'crop': crop_name,
        'overall_score': overall_score,
        'details': details
    }

@app.route('/')
def home():
    # Render Dashboard homepage
    crops_count = len(crop_stats) if crop_stats else 0
    return render_template('index.html', crops_count=crops_count)

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')

@app.route('/suitability')
def suitability():
    crops = sorted(list(crop_stats.keys())) if crop_stats else []
    return render_template('suitability.html', crops=crops)

@app.route('/research')
def research():
    return render_template('research.html')

@app.route('/disease-detection')
def disease_detection():
    return render_template('disease.html')

# API Endpoints
@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    if not model:
        return jsonify({'error': 'Machine learning model is not loaded.'}), 500
    
    try:
        data = request.json
        n = float(data.get('N'))
        p = float(data.get('P'))
        k = float(data.get('K'))
        temp = float(data.get('temperature'))
        hum = float(data.get('humidity'))
        ph = float(data.get('ph'))
        rain = float(data.get('rainfall'))
        
        validation_error = validate_crop_inputs({
            "N": n,
            "P": p,
            "K": k,
            "temperature": temp,
            "humidity": hum,
            "ph": ph,
            "rainfall": rain,
        })

        if validation_error:
            return jsonify({"error": validation_error}), 400

        
        # Predict using trained model
        input_data = [[n, p, k, temp, hum, ph, rain]]
        prediction = model.classes_[np.argmax(model.predict_proba(input_data)[0])]

        # Get probabilities for all crop classes
        probabilities = model.predict_proba(input_data)[0]
        top_indices = np.argsort(probabilities)[::-1][:3]

        # Prepare Top 3 crop recommendations
        top_crops = []

        for idx in top_indices:
            crop_name = model.classes_[idx]
            crop_confidence = round(float(probabilities[idx]) * 100, 2)

            crop_suitability = calculate_suitability(
                crop_name, n, p, k, temp, hum, ph, rain
            )

            top_crops.append({
                "crop": str(crop_name).capitalize(),
                "confidence": crop_confidence,
                "suitability_score": (
                    crop_suitability["overall_score"]
                    if crop_suitability else 100.0
                )
            })

            # Keep the existing primary crop and confidence
        class_idx = np.where(model.classes_ == prediction)[0][0]
        confidence = round(float(probabilities[class_idx]) * 100, 2)

        
            # Get suitability details of the recommended crop
        suitability_details = calculate_suitability(prediction, n, p, k, temp, hum, ph, rain)
        
        return jsonify({
            'crop': prediction.capitalize(),
            'confidence': confidence,
            'suitability_score': suitability_details['overall_score'] if suitability_details else 100.0,
            'details': suitability_details['details'] if suitability_details else {},
            'top_crops': top_crops
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/suitability', methods=['POST'])
def api_suitability():
    try:
        data = request.json
        crop_name = data.get('crop').lower()
        n = float(data.get('N'))
        p = float(data.get('P'))
        k = float(data.get('K'))
        temp = float(data.get('temperature'))
        hum = float(data.get('humidity'))
        ph = float(data.get('ph'))
        rain = float(data.get('rainfall'))

        validation_error = validate_crop_inputs({
            "N": n,
            "P": p,
            "K": k,
            "temperature": temp,
            "humidity": hum,
            "ph": ph,
            "rainfall": rain,
        })

        if validation_error:
            return jsonify({"error": validation_error}), 400
        
        result = calculate_suitability(crop_name, n, p, k, temp, hum, ph, rain)
        if not result:
            return jsonify({'error': f"No statistics found for crop: {crop_name}"}), 404
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/research-data')
def api_research_data():
    if not os.path.exists(DATA_PATH):
        return jsonify({'error': 'Dataset not found.'}), 404
        
    try:
        df = pd.read_csv(DATA_PATH)
        
        # Calculate mean requirement per crop
        crop_means = df.groupby('label').mean().reset_index()
        
        # Correlation matrix data
        features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        corr_matrix = df[features].corr().values.tolist()
        
        # Prepare crop profiles
        crop_list = crop_means['label'].tolist()
        means_data = {feat: crop_means[feat].tolist() for feat in features}
        
        # Classification of Soil Groups for policymakers
        # E.g., categorizing crops by water requirement, pH preference, N-requirement
        water_req = df.groupby('label')['rainfall'].mean().sort_values()
        ph_req = df.groupby('label')['ph'].mean().sort_values()
        
        soil_groups = {
            'drought_tolerant': [crop.capitalize() for crop in water_req[water_req < 80].index],
            'water_loving': [crop.capitalize() for crop in water_req[water_req > 150].index],
            'acidic_tolerant': [crop.capitalize() for crop in ph_req[ph_req < 6.0].index],
            'alkaline_tolerant': [crop.capitalize() for crop in ph_req[ph_req > 7.0].index],
        }
        
        return jsonify({
            'crops': [c.capitalize() for c in crop_list],
            'means': means_data,
            'features': features,
            'correlation': corr_matrix,
            'soil_groups': soil_groups
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv')
def export_csv():
    if not os.path.exists(DATA_PATH):
        return jsonify({'error': 'Dataset not found.'}), 404
        
    try:
        import io
        df = pd.read_csv(DATA_PATH)
        # Summarize crop conditions
        summary = df.groupby('label').mean().reset_index()
        summary.columns = ['Crop', 'Avg Nitrogen (N)', 'Avg Phosphorus (P)', 'Avg Potassium (K)', 
                           'Avg Temperature (°C)', 'Avg Humidity (%)', 'Avg pH', 'Avg Rainfall (mm)']
        
        output = io.BytesIO()
        summary.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name="crop_environmental_requirements.csv")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def api_health():
    is_crop_model_ready = model is not None
    is_disease_ready = (disease_detector is not None and getattr(disease_detector, 'model', None) is not None)
    crop_info = {
        'loaded': is_crop_model_ready,
        'type': 'Random Forest Classifier (multiclass)',
        'classes_count': len(model.classes_) if is_crop_model_ready else 0,
        'samples': 2200,
        'features': ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    }
    disease_info = {
        'loaded': is_disease_ready,
        'architecture': 'MobileNetV2 (Transfer Learning / Benchmark Pathology)',
        'classes_count': 38
    }
    return jsonify({
        'status': 'online' if is_crop_model_ready else 'degraded',
        'engine': 'active',
        'crop_recommendation_model': crop_info,
        'plant_disease_model': disease_info,
        'models': {
            'crop_recommendation_model': crop_info,
            'plant_disease_model': disease_info
        }
    })

@app.route('/api/model-evaluation')
def api_model_evaluation():
    if os.path.exists(EVAL_PATH):
        try:
            with open(EVAL_PATH, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': f'Failed to load evaluation metrics: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Evaluation metrics file not found. Run model_evaluation.py first.'}), 404

@app.route('/api/disease-detection', methods=['POST'])
def api_disease_detection():
    global disease_detector
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded.'}), 400
    
    file = request.files['image']
    if not file or file.filename == '':
        return jsonify({'error': 'Empty filename or invalid upload.'}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        return jsonify({'error': 'Invalid image format. Supported formats are JPG, PNG, and WebP.'}), 400

    try:
        image_bytes = file.read()
        if len(image_bytes) > 10 * 1024 * 1024:
            return jsonify({'error': 'File size exceeds maximum allowed limit of 10 MB.'}), 400
            
        if disease_detector is None:
            try:
                from disease_model import PlantDiseaseDetector
                disease_detector = PlantDiseaseDetector.get_instance()
            except Exception as e:
                return jsonify({'error': f'Disease diagnosis engine failed to initialize: {str(e)}'}), 500

        selected_plant = request.form.get('selected_plant') or request.form.get('plant_species') or None
        result = disease_detector.predict(image_bytes, selected_plant=selected_plant)
        if not result.get('success'):
            error_msg = result.get('error', 'Prediction failed.')
            # Surface validation failures clearly; hide internal paths/traces
            if result.get('validation_failed'):
                return jsonify({
                    'error': error_msg,
                    'validation_failed': True,
                    'plant_score': result.get('plant_score', 0.0),
                    'nonplant_score': result.get('nonplant_score', 0.0),
                    'top_imagenet': result.get('top_imagenet', [])
                }), 400
            return jsonify({'error': error_msg}), 400
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Server error processing diagnosis: {str(e)}'}), 500

@app.route('/api/disease-classes')
def api_disease_classes():
    try:
        from disease_model import get_supported_classes, SUPPORTED_PLANTS, CLASS_NAMES
        catalog = get_supported_classes()
        species_summary = [
            {
                'species': sp,
                'scientific_name': data['scientific_name'],
                'classes_count': len(data['classes']),
                'classes': data['classes']
            }
            for sp, data in sorted(SUPPORTED_PLANTS.items())
        ]
        return jsonify({
            'success': True,
            'total_classes': 38,
            'classes': CLASS_NAMES,
            'total_species': len(SUPPORTED_PLANTS),
            'catalog': catalog,
            'supported_species': species_summary,
            'unsupported_notice': (
                "OptiCrop's vision model is trained strictly on 14 crop species and 38 conditions from the PlantVillage benchmark. "
                "Crops outside this taxonomy (e.g. Pear, Rice, Wheat, Cotton) are unsupported and cannot be diagnosed."
            )
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-crops')
def api_compare_crops():
    crop1 = request.args.get('crop1', '').strip().lower()
    crop2 = request.args.get('crop2', '').strip().lower()
    
    if not crop_stats or crop1 not in crop_stats or crop2 not in crop_stats:
        return jsonify({'error': 'Please provide two valid model-supported crops to compare.'}), 400

    units = {
        'N': 'kg/ha',
        'P': 'kg/ha',
        'K': 'kg/ha',
        'temperature': '°C',
        'humidity': '%',
        'ph': 'pH units',
        'rainfall': 'mm'
    }
    
    param_names = {
        'N': 'Nitrogen',
        'P': 'Phosphorus',
        'K': 'Potassium',
        'temperature': 'Temperature',
        'humidity': 'Relative Humidity',
        'ph': 'Soil pH',
        'rainfall': 'Annual Rainfall'
    }

    comparison = {}
    c1_stats = crop_stats[crop1]
    c2_stats = crop_stats[crop2]
    
    insights = []
    
    for feat in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']:
        s1 = c1_stats[feat]
        s2 = c2_stats[feat]
        
        diff = round(s1['mean'] - s2['mean'], 2)
        pct_diff = round((diff / s2['mean']) * 100, 1) if s2['mean'] != 0 else 0
        
        comparison[feat] = {
            'param_name': param_names[feat],
            'unit': units[feat],
            'crop1': {
                'mean': round(s1['mean'], 2),
                'min': round(s1['min'], 2),
                'max': round(s1['max'], 2),
                'optimal_range': f"{round(s1['p10'], 1)} - {round(s1['p90'], 1)}"
            },
            'crop2': {
                'mean': round(s2['mean'], 2),
                'min': round(s2['min'], 2),
                'max': round(s2['max'], 2),
                'optimal_range': f"{round(s2['p10'], 1)} - {round(s2['p90'], 1)}"
            },
            'difference': diff,
            'percent_diff': pct_diff
        }

    rain_diff = round(c1_stats['rainfall']['mean'] - c2_stats['rainfall']['mean'], 1)
    if abs(rain_diff) > 20:
        higher_crop = crop1.capitalize() if rain_diff > 0 else crop2.capitalize()
        lower_crop = crop2.capitalize() if rain_diff > 0 else crop1.capitalize()
        insights.append(f"{higher_crop} demands substantially higher water intake (+{abs(rain_diff)} mm avg) than {lower_crop}, making it more water-intensive.")

    n_diff = round(c1_stats['N']['mean'] - c2_stats['N']['mean'], 1)
    if abs(n_diff) > 20:
        higher_crop = crop1.capitalize() if n_diff > 0 else crop2.capitalize()
        lower_crop = crop2.capitalize() if n_diff > 0 else crop1.capitalize()
        insights.append(f"{higher_crop} requires heavier nitrogen fertilization (+{abs(n_diff)} kg/ha avg) compared to {lower_crop}.")

    ph1 = c1_stats['ph']['mean']
    ph2 = c2_stats['ph']['mean']
    if abs(ph1 - ph2) > 0.5:
        insights.append(f"Soil acidity requirements diverge: {crop1.capitalize()} centers around pH {round(ph1, 1)}, while {crop2.capitalize()} prefers pH {round(ph2, 1)}.")

    return jsonify({
        'crop1': crop1.capitalize(),
        'crop2': crop2.capitalize(),
        'parameters': comparison,
        'insights': insights
    })

@app.route('/api/what-if', methods=['POST'])
def api_what_if():
    if not model:
        return jsonify({'error': 'Machine learning model is not loaded.'}), 500
    try:
        data = request.json or {}
        orig = data.get('original') or data.get('baseline') or {}
        mod = data.get('modified') or data.get('scenario') or {}
        
        for label, d in [('original', orig), ('modified', mod)]:
            err = validate_crop_inputs(d)
            if err:
                return jsonify({'error': f"Validation error in {label} values: {err}"}), 400
                
        def get_pred_bundle(inp):
            vals = [float(inp['N']), float(inp['P']), float(inp['K']), float(inp['temperature']), float(inp['humidity']), float(inp['ph']), float(inp['rainfall'])]
            probs = model.predict_proba([vals])[0]
            top_indices = np.argsort(probs)[::-1][:3]
            top_crops = []
            for idx in top_indices:
                c_name = model.classes_[idx]
                c_conf = round(float(probs[idx]) * 100, 2)
                suit = calculate_suitability(c_name, *vals)
                top_crops.append({
                    'crop': str(c_name).capitalize(),
                    'confidence': c_conf,
                    'suitability_score': suit['overall_score'] if suit else 100.0
                })
            top_crop = model.classes_[top_indices[0]]
            suit_top = calculate_suitability(top_crop, *vals)
            return {
                'crop': str(top_crop).capitalize(),
                'confidence': round(float(probs[top_indices[0]]) * 100, 2),
                'suitability_score': suit_top['overall_score'] if suit_top else 100.0,
                'top_3': top_crops,
                'top_crops': top_crops,
                'inputs': {
                    'N': float(inp['N']), 'P': float(inp['P']), 'K': float(inp['K']),
                    'temperature': float(inp['temperature']), 'humidity': float(inp['humidity']),
                    'ph': float(inp['ph']), 'rainfall': float(inp['rainfall'])
                }
            }
            
        orig_res = get_pred_bundle(orig)
        mod_res = get_pred_bundle(mod)
        
        deltas = {}
        changed = []
        feat_units = {'N': 'mg/kg', 'P': 'mg/kg', 'K': 'mg/kg', 'temperature': '°C', 'humidity': '%', 'ph': 'units', 'rainfall': 'mm'}
        param_labels = {
            'N': 'Nitrogen (N)', 'P': 'Phosphorus (P)', 'K': 'Potassium (K)',
            'temperature': 'Temperature', 'humidity': 'Humidity',
            'ph': 'Soil pH', 'rainfall': 'Rainfall'
        }
        for f in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']:
            d_val = round(mod_res['inputs'][f] - orig_res['inputs'][f], 2)
            deltas[f] = d_val
            if abs(d_val) > 0.001:
                changed.append({'feature': f, 'delta': d_val, 'unit': feat_units[f]})
                
        explanation_points = []
        if orig_res['crop'] != mod_res['crop']:
            explanation_points.append(f"Predicted crop shifted from {orig_res['crop']} ({orig_res['confidence']}%) to {mod_res['crop']} ({mod_res['confidence']}%) due to altered environmental parameters.")
        else:
            explanation_points.append(f"Primary prediction remained {orig_res['crop']}, with confidence adjusting from {orig_res['confidence']}% to {mod_res['confidence']}%.")
            
        for ch in changed:
            f = ch['feature']
            d = ch['delta']
            sign = "+" if d > 0 else ""
            explanation_points.append(f"Adjusted {param_labels[f]}: {sign}{d} {ch['unit']}.")

        input_differences = []
        for f in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']:
            d_val = deltas[f]
            input_differences.append({
                'parameter': param_labels[f],
                'feature': f,
                'baseline': orig_res['inputs'][f],
                'modified': mod_res['inputs'][f],
                'delta': d_val,
                'unit': feat_units[f],
                'feature_importance_rank': 'Dominant Climate Driver' if f in ['rainfall', 'humidity'] else 'Soil/Nutrient Factor'
            })
            
        disclaimer_text = "Random Forest model outputs represent statistical classifications on historical benchmark data. They do not simulate physical plant causality or guarantee real-world agricultural yield."
        return jsonify({
            'success': True,
            'original': orig_res,
            'modified': mod_res,
            'original_prediction': orig_res,
            'scenario_prediction': mod_res,
            'baseline': orig_res,
            'scenario': mod_res,
            'deltas': deltas,
            'changed_count': len(changed),
            'changed_inputs': changed,
            'input_differences': input_differences,
            'explanation': {
                'summary': " ".join(explanation_points),
                'key_drivers': explanation_points
            },
            'disclaimer': disclaimer_text,
            'statistical_disclaimer': disclaimer_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/multi-crop-suitability', methods=['POST'])
def api_multi_crop_suitability():
    if not crop_stats:
        return jsonify({'error': 'Crop statistics not loaded.'}), 500
    try:
        data = request.json or {}
        n = float(data.get('N'))
        p = float(data.get('P'))
        k = float(data.get('K'))
        temp = float(data.get('temperature'))
        hum = float(data.get('humidity'))
        ph = float(data.get('ph'))
        rain = float(data.get('rainfall'))
        
        val_err = validate_crop_inputs({"N": n, "P": p, "K": k, "temperature": temp, "humidity": hum, "ph": ph, "rainfall": rain})
        if val_err:
            return jsonify({'error': val_err}), 400
            
        requested_crops = data.get('crops', [])
        if not requested_crops:
            target_crops = list(crop_stats.keys())
        else:
            target_crops = [str(c).lower() for c in requested_crops if str(c).lower() in crop_stats]
            
        results = []
        for c in target_crops:
            suit = calculate_suitability(c, n, p, k, temp, hum, ph, rain)
            if not suit:
                continue
            details = suit['details']
            sorted_params = sorted(details.items(), key=lambda item: item[1]['score'])
            worst_param, worst_info = sorted_params[0]
            
            score = suit['overall_score']
            if score >= 80.0 and worst_info['score'] >= 30.0:
                compat = 'Suitable'
                compat_badge = 'success'
            elif score >= 50.0:
                compat = 'Partially Suitable'
                compat_badge = 'warning'
            else:
                compat = 'Unsuitable'
                compat_badge = 'danger'
                
            limiting_reason = f"{worst_param.capitalize()} ({worst_info['current']}) is {worst_info['status'].lower()} compared to optimal ({worst_info['optimal_range']})."
            
            results.append({
                'crop': c.capitalize(),
                'overall_score': score,
                'suitability_score': score,
                'compatibility': compat,
                'classification': compat,
                'compat_badge': compat_badge,
                'classification_color': compat_badge,
                'limiting_parameter': worst_param,
                'limiting_factor': limiting_reason,
                'primary_limiting_factor': limiting_reason,
                'details': details
            })
            
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'crops_evaluated': len(results),
            'total_crops_evaluated': len(results),
            'ranked_crops': results,
            'scoring_methodology': {
                'formula': 'Piecewise linear suitability: S_i = 100% within [p10, p90], linearly decaying towards min/max. Overall Score = (1/7) * sum(S_i).',
                'notice': 'Suitability assesses environmental requirement alignment based on ICFA crop trial statistics. It is distinct from machine-learning prediction probabilities.'
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/farm-health-summary', methods=['GET', 'POST'])
def api_farm_health_summary():
    try:
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form.to_dict() or {}
        else:
            data = request.args
            
        if not data or 'N' not in data:
            return jsonify({
                'has_data': False,
                'message': 'No soil or climatic parameters provided. Please input soil measurements or load an empirical profile.'
            })
            
        n = float(data.get('N'))
        p = float(data.get('P'))
        k = float(data.get('K'))
        temp = float(data.get('temperature'))
        hum = float(data.get('humidity'))
        ph = float(data.get('ph'))
        rain = float(data.get('rainfall'))
        
        err = validate_crop_inputs({"N": n, "P": p, "K": k, "temperature": temp, "humidity": hum, "ph": ph, "rainfall": rain})
        if err:
            return jsonify({'error': err}), 400
            
        alerts = []
        actions = []
        
        # Nutrient scoring
        n_status, n_color, n_score = ('Optimal', 'success', 100) if 50 <= n <= 100 else (('Low', 'warning', 60) if 20 <= n < 50 else (('Critically Low', 'danger', 20) if n < 20 else ('High', 'warning', 70)))
        if n < 30:
            alerts.append({'type': 'danger', 'title': 'Severe Nitrogen Deficit', 'desc': f'Soil N is {n} mg/kg (optimal: 50-100 mg/kg). Plants will suffer stunted vegetative growth and foliar chlorosis.'})
            actions.append('Apply organic compost, well-rotted manure, or split urea fertilizer before planting.')
        elif n > 120:
            alerts.append({'type': 'warning', 'title': 'Excess Soil Nitrogen', 'desc': f'Soil N is {n} mg/kg. Excessive vegetative growth increases lodging risk and delays flowering.'})
            
        p_status, p_color, p_score = ('Optimal', 'success', 100) if 30 <= p <= 70 else (('Low', 'warning', 60) if 15 <= p < 30 else (('Critically Low', 'danger', 20) if p < 15 else ('High', 'warning', 75)))
        if p < 20:
            alerts.append({'type': 'warning', 'title': 'Phosphorus Deficiency', 'desc': f'Soil P is {p} mg/kg (optimal: 30-70 mg/kg). Root development and early seedling vigor will be restricted.'})
            actions.append('Incorporate rock phosphate or DAP at planting into the root zone.')
            
        k_status, k_color, k_score = ('Optimal', 'success', 100) if 30 <= k <= 80 else (('Low', 'warning', 60) if 15 <= k < 30 else (('Critically Low', 'danger', 20) if k < 15 else ('High', 'warning', 75)))
        if k < 25:
            alerts.append({'type': 'warning', 'title': 'Potassium Deficit', 'desc': f'Soil K is {k} mg/kg (optimal: 30-80 mg/kg). Reduces drought tolerance and disease resistance.'})
            actions.append('Apply potassium sulfate or muriate of potash to enhance plant cellular turgor.')
            
        # pH
        if ph < 5.5:
            ph_status, ph_color, ph_score = 'Strongly Acidic', 'danger', 30
            alerts.append({'type': 'danger', 'title': 'Root-Zone Acidification Alert', 'desc': f'Soil pH {ph} leads to aluminum toxicity and binds available phosphorus.'})
            actions.insert(0, f'Apply agricultural lime (calcium carbonate) at 2-3 tons/ha to raise soil pH toward 6.5.')
        elif ph < 6.0:
            ph_status, ph_color, ph_score = 'Moderately Acidic', 'warning', 70
        elif ph <= 7.2:
            ph_status, ph_color, ph_score = 'Optimal Agronomic Range', 'success', 100
        elif ph <= 8.0:
            ph_status, ph_color, ph_score = 'Moderately Alkaline', 'warning', 70
        else:
            ph_status, ph_color, ph_score = 'Strongly Alkaline', 'danger', 35
            alerts.append({'type': 'danger', 'title': 'High Soil Alkalinity', 'desc': f'Soil pH {ph} locks micronutrients (Iron, Zinc, Manganese) causing interveinal chlorosis.'})
            actions.insert(0, 'Incorporate elemental sulfur or gypsum to gradually reduce root-zone alkalinity.')
            
        # Moisture & Disease Climate Risk
        if hum > 80 and 20 <= temp <= 30:
            clim_status, clim_color, clim_score = 'High Foliar Pathogen Risk', 'warning', 60
            alerts.append({'type': 'warning', 'title': 'Elevated Fungal Spore Hazard', 'desc': f'High humidity ({hum}%) paired with warm temperatures ({temp}°C) accelerates foliar fungal and bacterial blight sporulation.'})
            actions.append('Scout lower canopy weekly for early leaf spot lesions; prioritize drip irrigation over overhead sprinklers.')
        elif hum < 40 and rain < 70:
            clim_status, clim_color, clim_score = 'High Drought/Moisture Stress', 'warning', 60
            alerts.append({'type': 'warning', 'title': 'Evapotranspiration Deficit', 'desc': f'Rainfall ({rain} mm) and humidity ({hum}%) indicate significant crop water stress.'})
            actions.append('Apply surface mulch to conserve soil moisture and plan deficit irrigation schedules.')
        else:
            clim_status, clim_color, clim_score = 'Balanced Growing Climate', 'success', 100
            
        if not actions:
            actions.append('Maintain current balanced soil fertility and periodic scouting.')
            
        health_score = round(0.4 * ((n_score + p_score + k_score) / 3.0) + 0.3 * ph_score + 0.3 * clim_score, 1)
        
        return jsonify({
            'has_data': True,
            'health_score': health_score,
            'health_rating': 'Excellent' if health_score >= 85 else ('Good' if health_score >= 70 else ('Fair' if health_score >= 50 else 'Critical Attention Needed')),
            'nutrients': {
                'N': {'value': n, 'unit': 'mg/kg', 'status': n_status, 'color': n_color, 'optimal': '50 - 100'},
                'P': {'value': p, 'unit': 'mg/kg', 'status': p_status, 'color': p_color, 'optimal': '30 - 70'},
                'K': {'value': k, 'unit': 'mg/kg', 'status': k_status, 'color': k_color, 'optimal': '30 - 80'}
            },
            'ph': {'value': ph, 'status': ph_status, 'color': ph_color, 'optimal': '6.0 - 7.2'},
            'climate': {'temperature': temp, 'humidity': hum, 'rainfall': rain, 'status': clim_status, 'color': clim_color},
            'alerts': alerts,
            'prioritized_actions': actions[:4],
            'methodology': 'Composite agro-ecological formula: Health Score = 40% (NPK Balance) + 30% (pH Compatibility) + 30% (Climate Moisture Risk).'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/disease-evaluation', methods=['GET'])
def api_disease_evaluation():
    paths_to_try = [
        os.path.join(BASE_DIR, "config", "disease_evaluation.json"),
        os.path.join(BASE_DIR, "training", "training_output", "disease_evaluation.json"),
        os.path.join(PROJECT_ROOT, "backend", "config", "disease_evaluation.json"),
        os.path.join(BASE_DIR, "disease_evaluation.json"),
        os.path.join(PROJECT_ROOT, "disease_evaluation.json"),
        os.path.join(PROJECT_ROOT, "training_output", "disease_evaluation.json")
    ]
    eval_path = None
    for p in paths_to_try:
        if os.path.exists(p):
            eval_path = p
            break

    if eval_path:
        try:
            with open(eval_path, 'r') as f:
                data = json.load(f)
            return jsonify({
                'success': True,
                'model': data.get('model', 'MobileNetV2'),
                'dataset': data.get('dataset', 'PlantVillage Benchmark'),
                'test_samples': data.get('test_samples', 731),
                'num_classes': data.get('num_classes', 38),
                'metrics': data.get('metrics', {}),
                'per_class_metrics': data.get('per_class_metrics', {}),
                'benchmark_notice': 'Metrics evaluated on controlled PlantVillage single-leaf test imagery. Does not reflect unmeasured in-field real-world diagnostic accuracy under complex natural lighting, shaded canopies, or multiple simultaneous infections.'
            })
        except Exception as e:
            return jsonify({'error': f'Failed to read disease evaluation: {str(e)}'}), 500
    return jsonify({
        'success': False,
        'error': 'Disease evaluation data not found.',
        'metrics': {},
        'per_class_metrics': {}
    }), 404

@app.route('/api/benchmark-latency', methods=['GET', 'POST'])
def api_benchmark_latency():
    try:
        import time
        results = {}
        
        # 1. Benchmark Tabular Random Forest Crop Recommendation Model
        if model is not None:
            rf_latencies = []
            sample_df = pd.DataFrame([{
                'N': 90.0, 'P': 42.0, 'K': 43.0,
                'temperature': 20.87, 'humidity': 82.0,
                'ph': 6.5, 'rainfall': 202.9
            }])
            for _ in range(2):
                model.predict_proba(sample_df)
            for _ in range(10):
                t0 = time.perf_counter()
                model.predict_proba(sample_df)
                t1 = time.perf_counter()
                rf_latencies.append((t1 - t0) * 1000.0)
            
            results['crop_model'] = {
                'name': 'Random Forest (100 Trees)',
                'task': 'Tabular Crop Recommendation (22 Classes)',
                'iterations': 10,
                'mean_ms': round(float(np.mean(rf_latencies)), 2),
                'min_ms': round(float(np.min(rf_latencies)), 2),
                'max_ms': round(float(np.max(rf_latencies)), 2),
                'throughput_fps': round(1000.0 / float(np.mean(rf_latencies)), 1) if np.mean(rf_latencies) > 0 else 0
            }
            
        # 2. Benchmark Vision MobileNetV2 Disease Model
        global disease_detector
        if disease_detector is None:
            try:
                from disease_model import PlantDiseaseDetector
                disease_detector = PlantDiseaseDetector.get_instance()
            except Exception:
                disease_detector = None

        if disease_detector is not None and getattr(disease_detector, 'session', None) is not None:
            cv_latencies = []
            session = disease_detector.session
            in_name = session.get_inputs()[0].name
            dummy_tensor = np.zeros((1, 3, 224, 224), dtype=np.float32)
            for _ in range(1):
                session.run(None, {in_name: dummy_tensor})
            for _ in range(5):
                t0 = time.perf_counter()
                session.run(None, {in_name: dummy_tensor})
                t1 = time.perf_counter()
                cv_latencies.append((t1 - t0) * 1000.0)
                
            results['disease_model'] = {
                'name': 'MobileNetV2 (ONNX Runtime CPU)',
                'task': 'Computer Vision Foliar Pathology (38 Classes)',
                'input_shape': '1x3x224x224 (RGB Tensor)',
                'iterations': 5,
                'mean_ms': round(float(np.mean(cv_latencies)), 2),
                'min_ms': round(float(np.min(cv_latencies)), 2),
                'max_ms': round(float(np.max(cv_latencies)), 2),
                'throughput_fps': round(1000.0 / float(np.mean(cv_latencies)), 1) if np.mean(cv_latencies) > 0 else 0
            }
        
        return jsonify({
            'success': True,
            'benchmarks': results,
            'environment': 'Production CPU Execution Provider'
        })
    except Exception as e:
        return jsonify({'error': f'Latency benchmark encountered an error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

