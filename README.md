# OptiCrop — Smart Agricultural Production Optimization Engine

> **Precision Machine Learning for Sustainable Farming**

OptiCrop is a full-stack agricultural AI application that integrates crop recommendation, soil suitability analysis, plant disease detection, and research analytics into a unified web platform. It leverages scikit-learn and PyTorch-based models to deliver actionable insights for farmers, researchers, and agronomists.

---

## Features

### 1. Crop Recommendation Engine
- Input 7 soil and climate parameters (N, P, K, Temperature, Humidity, pH, Rainfall)
- Random Forest classifier trained on 2,200 samples across **22 crop categories**
- **Top-3 ranked recommendations** with confidence scores
- Real-time weather autofill via Open-Meteo API (free, no API key required)
- Preset soil profiles for quick testing
- Input validation with agronomic range limits

### 2. Soil Suitability Analysis
- Evaluate soil compatibility against a target crop
- Radar chart comparison of actual vs. ideal nutrient profiles
- Per-parameter suitability scores and agronomic correction suggestions
- Environmental requirements from curated CSV reference data

### 3. AI Plant Disease Detection
- **MobileNetV2** convolutional neural network for leaf image classification
- Supports **38 plant disease classes** across 14 crop species (PlantVillage benchmark)
- Drag-and-drop image upload with real-time preview
- **Out-of-Distribution (OOD) guardrails**: entropy-based confidence tiering and warnings for uncertain predictions
- Actionable care guidance (symptoms, treatment, prevention) for every detected disease
- AI disclaimer for responsible use

### 4. Research & Model Analytics
- True Random Forest evaluation metrics (precision, recall, F1, confusion matrix)
- Feature importance rankings
- Per-crop nutrient distribution analysis
- Crop-vs-crop comparison tools
- Interactive Chart.js visualizations

### 5. Dashboard
- System health overview with ML engine status
- Crops tracked, model accuracy, inference time stats
- Quick-link scenario cards to all features
- Global search across all application sections

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.x, Flask |
| Crop ML | scikit-learn (Random Forest), joblib |
| Disease ML | PyTorch, torchvision (MobileNetV2) |
| Frontend | HTML5, CSS3, JavaScript (ES6) |
| Charts | Chart.js |
| Weather | Open-Meteo API (free, keyless) |
| Icons | Font Awesome 6 |

---

## Project Structure

```
opticrop/
├── app.py                          # Flask application (5 page routes + 9 API routes)
├── model.py                        # Crop recommendation model training script
├── model_evaluation.py             # Crop model evaluation and metrics generation
├── disease_model.py                # Plant disease detection (MobileNetV2 inference + OOD)
├── train_disease_model.py          # Disease model training pipeline
├── convert_to_onnx.py              # PyTorch-to-ONNX model conversion
├── crop_recommendation_model.pkl   # Trained Random Forest model
├── plant_disease_mobilenet_v2.pth  # MobileNetV2 weights (38 classes)
├── Crop_recommendation.csv         # Crop dataset (2200 rows × 8 columns)
├── crop_environmental_requirements.csv  # Ideal crop ranges reference
├── crop_stats.json                 # Per-crop statistical profiles
├── evaluation_metrics.json         # RF evaluation results (99.3% accuracy)
├── requirements.txt                # Python dependencies
├── tests.py                        # Comprehensive test suite (32 tests)
├── templates/
│   ├── base.html                   # Base layout with sidebar navigation
│   ├── index.html                  # Dashboard
│   ├── recommend.html              # Crop recommendation form
│   ├── suitability.html            # Suitability analysis form
│   ├── disease.html                # Disease detection upload interface
│   └── research.html               # Research analytics dashboard
├── static/
│   ├── css/style.css               # Application styles
│   └── js/main.js                  # Client-side logic (~63KB)
├── datasets/                       # PlantVillage training data
└── backup/                         # Model artifact backups
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/vijayatedlapu15/OptiCrop.git
cd OptiCrop

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application starts at **http://127.0.0.1:5000/**

---

## API Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard |
| GET | `/recommend` | Crop recommendation page |
| GET | `/suitability` | Suitability analysis page |
| GET | `/disease-detection` | Disease detection page |
| GET | `/research` | Research analytics page |
| GET | `/api/health` | Engine health check |
| POST | `/api/predict` | Crop prediction (JSON) |
| POST | `/api/suitability` | Suitability analysis (JSON) |
| POST | `/api/detect-disease` | Disease detection (multipart image) |
| GET | `/api/research-data` | Research statistics |
| GET | `/api/model-evaluation` | Model evaluation metrics |
| GET | `/api/disease-classes` | Disease class listing |
| GET | `/api/crop-comparison` | Crop comparison data |
| GET | `/api/export-report` | CSV report export |

---

## Datasets

### Crop Recommendation
- **Source**: `Crop_recommendation.csv` (2,200 samples, 22 balanced classes × 100 samples each)
- **Features**: Nitrogen (N), Phosphorus (P), Potassium (K), Temperature, Humidity, pH, Rainfall
- **Target**: Crop label (22 categories)
- **Model**: Random Forest Classifier (100 estimators, `random_state=42`)
- **Accuracy**: 99.32% on held-out test set (80/20 split)

### Plant Disease Detection
- **Architecture**: MobileNetV2 (transfer learning)
- **Classes**: 38 plant disease/healthy categories from the [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset) benchmark
- **Supported crops**: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato
- **Weights**: Pre-trained checkpoint (`plant_disease_mobilenet_v2.pth`, 9.3 MB)
- **Note**: The existing weights were sourced from a third-party HuggingFace repository. For full provenance, use `train_disease_model.py` to retrain from scratch on the PlantVillage dataset.

---

## Testing

```bash
# Run the full test suite (32 tests)
python -m pytest tests.py -v --tb=short
```

Test coverage includes:
- Page route rendering (5 pages)
- Health endpoint and model loading
- Crop recommendation (valid/invalid inputs, edge cases)
- Suitability analysis
- Disease detection (image upload, invalid files)
- Research data endpoints
- CSV export

---

## Model Training

### Crop Recommendation Model
```bash
python model.py           # Train Random Forest
python model_evaluation.py # Generate evaluation metrics
```

### Disease Detection Model (Retraining)
```bash
# 1. Download PlantVillage dataset
python download_plantvillage.py

# 2. Train MobileNetV2
python train_disease_model.py

# 3. Evaluate only
python train_disease_model.py evaluate

# 4. Convert to ONNX (optional, for lightweight deployment)
python convert_to_onnx.py
```

---

## OOD (Out-of-Distribution) Handling

The disease detection system includes confidence safeguards:
- **High confidence (≥60%)**: Standard prediction with care guidance
- **Low confidence (40–60%)**: Warning that the prediction may be unreliable
- **Very low confidence (<40%)**: Strong warning advising professional consultation
- **High entropy**: Alert when the model is uncertain across multiple classes
- **AI disclaimer**: Every prediction includes a note that results are for preliminary assessment only

---

## Known Limitations

1. The disease model supports 14 crop species and 38 conditions. Images of unsupported crops may receive incorrect high-confidence predictions.
2. The current disease model weights are from a third-party source. Retraining with `train_disease_model.py` on the full PlantVillage dataset is recommended for full provenance.
3. PyTorch is ~800 MB, which exceeds Vercel's 250 MB serverless function limit. For serverless deployment, convert to ONNX format.
4. Weather autofill uses the Open-Meteo free API and may be rate-limited under heavy usage.

---

## License

This project is for educational and research purposes.

- **Crop dataset**: [Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) (public)
- **Disease dataset**: [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset) (CC0 1.0 Public Domain)
- **MobileNetV2**: [PyTorch torchvision models](https://pytorch.org/vision/stable/models.html) (BSD-3-Clause)

---

© 2026 OptiCrop — Smart Agricultural Production Optimization Engine
