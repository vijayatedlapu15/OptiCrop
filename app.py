import os
import json
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "crop_recommendation_model.pkl")
STATS_PATH = os.path.join(BASE_DIR, "crop_stats.json")
DATA_PATH = os.path.join(BASE_DIR, "Crop_recommendation.csv")
EVAL_PATH = os.path.join(BASE_DIR, "evaluation_metrics.json")

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
        df = pd.read_csv(DATA_PATH)
        # Summarize crop conditions
        summary = df.groupby('label').mean().reset_index()
        summary.columns = ['Crop', 'Avg Nitrogen (N)', 'Avg Phosphorus (P)', 'Avg Potassium (K)', 
                           'Avg Temperature (°C)', 'Avg Humidity (%)', 'Avg pH', 'Avg Rainfall (mm)']
        
        temp_file = "crop_environmental_requirements.csv"
        summary.to_csv(temp_file, index=False)
        
        return send_file(temp_file, as_attachment=True, download_name="crop_environmental_requirements.csv")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def api_health():
    is_crop_model_ready = model is not None
    is_disease_ready = (disease_detector is not None and getattr(disease_detector, 'model', None) is not None)
    return jsonify({
        'status': 'online' if is_crop_model_ready else 'degraded',
        'engine': 'active',
        'crop_recommendation_model': {
            'loaded': is_crop_model_ready,
            'type': 'Random Forest Classifier (multiclass)',
            'classes_count': len(model.classes_) if is_crop_model_ready else 0,
            'samples': 2200,
            'features': ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        },
        'plant_disease_model': {
            'loaded': is_disease_ready,
            'architecture': 'MobileNetV2 (Transfer Learning / Benchmark Pathology)',
            'classes_count': 38
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

        result = disease_detector.predict(image_bytes)
        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Prediction failed.')}), 400
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Server error processing diagnosis: {str(e)}'}), 500

@app.route('/api/disease-classes')
def api_disease_classes():
    try:
        from disease_model import get_supported_classes
        return jsonify({
            'success': True,
            'total_classes': 38,
            'catalog': get_supported_classes()
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
