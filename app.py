import os
import json
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# Paths
MODEL_PATH = "crop_recommendation_model.pkl"
STATS_PATH = "crop_stats.json"
DATA_PATH = "Crop_recommendation.csv"

# Global variables for model and stats
model = None
crop_stats = None

def load_resources():
    global model, crop_stats
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH, 'r') as f:
            crop_stats = json.load(f)

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
        
        # Predict using trained model
        input_data = [[n, p, k, temp, hum, ph, rain]]
        prediction = model.predict(input_data)[0]
        
        # Get probability/confidence
        probabilities = model.predict_proba(input_data)[0]
        class_idx = np.where(model.classes_ == prediction)[0][0]
        confidence = round(probabilities[class_idx] * 100, 2)
        
        # Get suitability details of the recommended crop
        suitability_details = calculate_suitability(prediction, n, p, k, temp, hum, ph, rain)
        
        return jsonify({
            'crop': prediction.capitalize(),
            'confidence': confidence,
            'suitability_score': suitability_details['overall_score'] if suitability_details else 100.0,
            'details': suitability_details['details'] if suitability_details else {}
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

if __name__ == '__main__':
    load_resources()
    app.run(debug=True, port=5000)
