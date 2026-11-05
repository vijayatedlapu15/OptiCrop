# OptiCrop — Smart Agricultural Production Optimization Engine

> **Precision Machine Learning for Sustainable Farming**

OptiCrop is a full-stack agricultural AI application that integrates crop recommendation, soil suitability analysis, plant disease detection, and research analytics into a unified web platform. It leverages scikit-learn and PyTorch-based models to deliver actionable insights for farmers, researchers, and agronomists.

---

## Features Across the Five Core Sections

### 1. Dashboard — Smart Farm Intelligence
- **Farm Health & Risk Summary**: Transparent 0-100 Farm Health Index (FHI) calculated via an explainable composite formula: 40% Macronutrient Balance (N, P, K) + 30% Root-zone pH Alignment + 30% Climate/Foliar Spore Pressure.
- **Empirical Soil Presets**: Instant evaluation against verified regional profiles (Alluvial Loam, Semi-Arid Maize, Acidic High-Rainfall, Alkaline Dryland) or custom field inputs.
- **Active Agro-Climatic Hazards**: Real-time alerts for elevated foliar fungal spore sporulation, evapotranspiration moisture deficits, and soil acidification.
- **Prioritized Action Plan**: Clear, actionable, ranked field interventions tailored to current soil and climate constraints.

### 2. Crop Recommend — What-If AI Simulator
- **Interactive Scenario Simulator**: Test hypothetical weather shifts, drought conditions, soil acidification, or nitrogen surges before applying in the field.
- **Side-by-Side ML Inference**: Direct comparison of baseline vs. modified scenario predictions powered by the real Random Forest classifier (`predict_proba`).
- **Feature Delta Tracking**: Visual difference badges tracking numerical and percentage shifts for all 7 soil and climate parameters.
- **Model Decision Explanations**: Explainable ML breakdown showing which parameter shifts drove the recommendation change based on tree Gini feature importances.
- **Top-3 Ranked Alternatives**: Realistic probability distributions without claiming guaranteed crop yield or causal outcomes.

### 3. Crop Suitability — Explainable Multi-Crop Comparison
- **Continuous Agro-Ecological Scoring**: Evaluates and ranks all 22 supported crops simultaneously using continuous piecewise linear suitability envelopes from ICFA benchmark data.
- **Primary Limiting Factor Callouts**: Explicitly identifies the single most restrictive environmental bottleneck for each crop (e.g., severe nitrogen deficit, excessive precipitation, suboptimal root-zone pH).
- **Interactive Deep-Dive**: Direct "Inspect" integration loading any ranked crop into the single-crop radar diagnostic view.
- **Clear Agronomic Explanations**: Transparent distinction between statistical machine-learning prediction probabilities and rule-based physiological suitability.

### 4. Plant Disease — Diagnosis, Management, Treatment & Recovery
- **MobileNetV2 Vision Screening**: Evaluated on the 38-class PlantVillage benchmark across 14 host crop species via ONNX Runtime CPU inference.
- **Host Species Compatibility Guardrails**: Explicit taxonomy matching preventing cross-species misdiagnoses (e.g., flagging peach leaves screened as tomato).
- **Responsible Uncertainty Gating**: Shannon entropy thresholding, softmax margin gating, and Laplacian texture variance filtering.
- **Comprehensive 38-Class Pathology Knowledge Base**: Structured, disease-specific profiles covering pathogen types (Fungal, Bacterial, Viral, Oomycete, Pest/Mite, Physiological) and causal organisms.
- **Safe & Evidence-Based Treatment Guidance**: Strict separation of cultural sanitation, biological controls, and verified chemical active ingredients. Never recommends fungicides for viral or bacterial conditions.
- **Mandatory Chemical Withholding**: Chemical sprays are strictly withheld whenever diagnostic uncertainty is detected or host species is incompatible.
- **Interactive Recovery Checklist**: Practical session checklist enabling farmers to track containment steps with live progress indicators.
- **Traceable Scientific Citations**: Authoritative references from UC IPM, Cornell Vegetable MD, Penn State Extension, University of Florida IFAS, and ICAR/KVK.

### 5. Research Analytics — Model Evaluation Lab
- **Dual-Model Performance Benchmarking**: True held-out test evaluation for both the Random Forest Crop Model (99.32% test accuracy, 440 samples) and the MobileNetV2 Disease Model (96.72% accuracy, 90.08% Macro F1, 731 test samples across 38 classes).
- **Controlled Lab vs. Real-World Field Reality**: Clear scientific documentation explaining why controlled single-leaf benchmark accuracy does not equate to open-field diagnostic accuracy under canopy clutter, specular glint, and multi-pathogen co-infections.
- **Interactive Per-Class Evaluation Table**: Searchable breakdown of precision, recall, F1-score, and support for all 38 foliar conditions.
- **Known Failure Modes**: Documented limitations including closed-set out-of-distribution vulnerability, abiotic vs. biotic symptom mimicry, and single-leaf staging bias.
- **Live Hardware Latency Benchmark**: Real-time measurement of model inference latency (mean, min, max ms) and throughput (FPS) executed directly on the host system.


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
├── disease_model.py                # Plant disease detection (MobileNetV2 ONNX inference + reliability guards)
├── train_disease_model.py          # Disease model training pipeline
├── convert_to_onnx.py              # PyTorch-to-ONNX model conversion
├── crop_recommendation_model.pkl   # Trained Random Forest model (3.4 MB)
├── plant_disease_model.onnx        # Exported MobileNetV2 ONNX model (8.85 MB)
├── class_mapping.json              # 38-class index-to-label mapping (1.4 KB)
├── Crop_recommendation.csv         # Crop dataset (2200 rows × 8 columns)
├── crop_environmental_requirements.csv  # Ideal crop ranges reference
├── crop_stats.json                 # Per-crop statistical profiles
├── evaluation_metrics.json         # RF evaluation results (99.32% test accuracy)
├── requirements.txt                # Python production dependencies
├── tests.py                        # Comprehensive test suite (32 tests)
├── test_reliability.py             # Reliability and uncertainty test suite (17 tests)
├── test_enhancements.py            # End-to-end ML enhancement verification suite
├── test_disease_fix.py             # Disease detection integration tests
├── templates/
│   ├── base.html                   # Base layout with sidebar navigation
│   ├── index.html                  # Dashboard
│   ├── recommend.html              # Crop recommendation form
│   ├── suitability.html            # Suitability analysis form
│   ├── disease.html                # Disease detection upload interface with species selector
│   └── research.html               # Research analytics dashboard
├── static/
│   ├── css/style.css               # Application styles
│   └── js/main.js                  # Client-side logic & Chart.js handlers
├── public/                         # Static CDN mirror for Vercel deployment
├── datasets/                       # PlantVillage training & evaluation data
└── training_output/                # Checkpoints & evaluation logs
```

---

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/vijayatedlapu15/OptiCrop.git
cd OptiCrop

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application locally
python app.py
```

The application starts at **http://127.0.0.1:5000/** (or custom `$PORT`).

---

## API Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard view |
| GET | `/recommend` | Crop recommendation interface |
| GET | `/suitability` | Soil suitability assessment interface |
| GET | `/disease-detection` | Plant disease diagnosis interface |
| GET | `/research` | Research analytics dashboard |
| GET | `/api/health` | Engine health status and model availability |
| POST | `/api/recommend` | Crop recommendation (7 soil/climate features in JSON) |
| POST | `/api/suitability` | Crop suitability analysis (target crop + soil features in JSON) |
| POST | `/api/disease-detection` | Foliar pathology diagnosis (multipart image + optional `selected_plant`) |
| GET | `/api/disease-classes` | Complete 38-class pathology taxonomy and 14 supported species |
| GET | `/api/research-data` | Empirical feature means, correlation matrix, and soil groupings |
| GET | `/api/compare-crops` | Pairwise agronomic comparison between two supported crops |
| GET | `/api/model-evaluation` | Random Forest held-out evaluation metrics |
| GET | `/api/export/csv` | In-memory CSV download of crop environmental requirements |

---

## Models and Benchmark Evaluation

### 1. Crop Recommendation Engine
- **Algorithm**: Random Forest Classifier (`n_estimators=100`, `random_state=42`)
- **Dataset**: `Crop_recommendation.csv` (2,200 samples across 22 balanced crop categories)
- **Features**: Nitrogen (N), Phosphorus (P), Potassium (K), Temperature (°C), Humidity (%), Soil pH, Annual Rainfall (mm)
- **Measured Evaluation**: **99.32% Accuracy** on 440 held-out test samples (80/20 train/test split)
- **Outputs**: Top-3 ranked crop predictions with probabilities, suitability assessment, and remediation advice.

### 2. Plant Disease Vision Classifier
- **Architecture**: MobileNetV2 (Transfer Learning from ImageNet)
- **Runtime**: ONNX Runtime (`plant_disease_model.onnx`, 8.85 MB) for fast CPU inference and serverless compliance
- **Provenance**: Trained on the peer-reviewed [PlantVillage](https://github.com/spMohanty/PlantVillage-Dataset) benchmark dataset
- **Measured Evaluation** (Held-Out Test Set, 731 samples across 38 classes):
  - **Accuracy**: $96.72\%$
  - **Macro Precision**: $92.00\%$
  - **Macro Recall**: $89.82\%$
  - **Macro F1 Score**: $90.08\%$
  - **Weighted F1 Score**: $96.71\%$
- **Benchmark Distinction**:
  > *Held-out benchmark metrics reflect performance on controlled, single-leaf imagery from the PlantVillage dataset. They do not represent unmeasured in-field diagnostic accuracy under complex canopy backgrounds, variable sunlight, multiple simultaneous infections, or unrepresented plant varieties.*

---

## Supported Plant Species & Pathology Taxonomy

OptiCrop is a closed-set classifier supporting exactly **14 host plant species** across **38 distinct condition classes**:

| Host Plant Species | Scientific Name | Classes Count | Conditions Covered |
| :--- | :--- | :---: | :--- |
| **Apple** | *Malus domestica* | 4 | Apple Scab, Black Rot, Cedar Apple Rust, Healthy |
| **Blueberry** | *Vaccinium corymbosum* | 1 | Healthy |
| **Cherry** | *Prunus avium / cerasus* | 2 | Powdery Mildew, Healthy |
| **Corn (Maize)** | *Zea mays* | 4 | Cercospora Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy |
| **Grape** | *Vitis vinifera* | 4 | Black Rot, Esca (Black Measles), Leaf Blight (Isariopsis), Healthy |
| **Orange** | *Citrus sinensis* | 1 | Huanglongbing (Citrus Greening) |
| **Peach** | *Prunus persica* | 2 | Bacterial Spot, Healthy |
| **Pepper (Bell)** | *Capsicum annuum* | 2 | Bacterial Spot, Healthy |
| **Potato** | *Solanum tuberosum* | 3 | Early Blight, Late Blight, Healthy |
| **Raspberry** | *Rubus idaeus* | 1 | Healthy |
| **Soybean** | *Glycine max* | 1 | Healthy |
| **Squash** | *Cucurbita pepo* | 1 | Powdery Mildew |
| **Strawberry** | *Fragaria × ananassa* | 2 | Leaf Scorch, Healthy |
| **Tomato** | *Solanum lycopersicum* | 10 | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Two-Spotted Spider Mites, Target Spot, Yellow Leaf Curl Virus (TYLCV), Mosaic Virus (ToMV), Healthy |

---

## Uncertainty & Reliability Safeguards

Because closed-set neural networks tend to assign high confidence to unfamiliar or unsupported inputs, OptiCrop incorporates multi-signal reliability guardrails:

1. **Host Species Compatibility Verification**:
   - Allows users to select their plant species prior to analysis.
   - If the predicted pathology conflicts with the selected plant (e.g. user selected *Apple*, model predicted *Corn Gray Leaf Spot*), the result is flagged as `incompatible` and never presented as a confirmed diagnosis.
2. **Multi-Signal Uncertainty Gating**:
   - **Confidence Threshold**: Predictions with model scores $<65\%$ are flagged as `uncertain`.
   - **Decision Margin**: Top-1 probability must exceed Top-2 probability by $\ge 15\%$.
   - **Full-Vector Shannon Entropy**: Normalized entropy across all 38 classes must remain $\le 0.50$:
     $$\hat{H}(p) = -\frac{1}{\ln(38)} \sum_{i=1}^{38} p_i \ln(p_i)$$
   - **Image Quality Validation**: Input images must have dimensions $\ge 32\times32\text{ px}$ and foliar pixel variance $\sigma \ge 10.0$ to reject blank, uniform, or degenerate uploads.
3. **Conditional Treatment Withholding**:
   - Disease-specific chemical fungicides and curative treatments are strictly withheld for `uncertain` or `incompatible` results. Safe general hygiene and extension consultation advice are provided instead.
4. **Transparent Scoring**:
   - Softmax outputs are explicitly documented as *"Model Confidence Scores"* (statistical distribution over 38 classes), not guaranteed clinical truth.

---

## Known Limitations

1. **Closed-Set Architectural Scope**:
   The model is strictly bounded to the 14 host crops and 38 conditions listed above. Foliage from unsupported crops (such as Pear, Quince, Rice, Wheat, Cotton) or unrepresented conditions (such as European Pear Rust, *Gymnosporangium sabinae*) cannot be diagnosed.
2. **Species Selection Verification**:
   Specifying a host species checks model compatibility, but the optical model cannot verify whether the uploaded leaf physically belongs to that species.
3. **Advisory Screening Only**:
   Computer vision leaf screening is an agronomic aid and does not substitute for laboratory phytopathological assays (PCR, ELISA, microscopic culture isolation). Consult a local agricultural extension specialist before applying chemical treatments.
4. **Weather Autofill Rate Limits**:
   Live weather autofill relies on the free Open-Meteo API without an API key; heavy concurrent requests may be subject to upstream rate limiting.

---

## Testing & Verification

```bash
# Run complete test suite (32 tests)
python -m pytest tests.py -v

# Run reliability & uncertainty verification suite (17 tests)
python -m pytest test_reliability.py -v

# Run ML enhancement verification suite (7 phases)
python test_enhancements.py

# Run disease detection integration suite
python test_disease_fix.py
```

---

## License

This project is for educational and research purposes.

- **Crop dataset**: [Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) (public)
- **Disease dataset**: [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset) (CC0 1.0 Public Domain)
- **MobileNetV2**: [PyTorch torchvision models](https://pytorch.org/vision/stable/models.html) (BSD-3-Clause)

---

© 2026 OptiCrop — Smart Agricultural Production Optimization Engine
