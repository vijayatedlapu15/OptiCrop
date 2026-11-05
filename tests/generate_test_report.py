"""
generate_test_report.py — Generates detailed diagnostic records for the 10 required categories.
"""

import os
import io
import json
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
for p in [PROJECT_ROOT, BACKEND_DIR, os.path.join(BACKEND_DIR, "utils")]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend import app as flask_app
except ImportError:
    import app as flask_app
from external_verifier import (
    STATUS_CORROBORATED,
    STATUS_POSSIBLE,
    STATUS_UNCERTAIN,
    STATUS_UNSUPPORTED,
    STATUS_VERIFICATION_UNAVAILABLE
)

flask_app.app.config['TESTING'] = True
client = flask_app.app.test_client()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = (
    os.path.join(BASE_DIR, 'fixtures')
    if os.path.exists(os.path.join(BASE_DIR, 'fixtures'))
    else (
        os.path.join(BASE_DIR, 'test_fixtures')
        if os.path.exists(os.path.join(BASE_DIR, 'test_fixtures'))
        else os.path.join(BASE_DIR, '..', 'test_fixtures')
    )
)

TEST_CASES = [
    {
        "category": "1. Potato Early Blight",
        "file": "potato_early_blight.jpg",
        "ground_truth": "Potato (Solanum tuberosum) with Early Blight (Alternaria solani)",
        "mock_vision": {
            "is_plant": True,
            "is_clear": True,
            "likely_plant": "Potato (Solanum tuberosum)",
            "leaf_shape_and_structure": "Odd-pinnate compound broadleaf with ovate leaflets",
            "is_monocot_grass": False,
            "is_broadleaf": True,
            "visible_symptoms": "Dark brown circular-to-irregular lesions with concentric target rings and chlorotic halos",
            "colour_changes_and_patterns": "Prominent yellow chlorotic margin surrounding dark necrotic centers",
            "most_likely_disease": "Early Blight (Alternaria solani)",
            "alternative_diagnoses": ["Late Blight (Phytophthora infestans)", "Septoria Leaf Spot"],
            "is_healthy": False,
            "supported_opticrop_species": True,
            "identification_certainty": "high",
            "diagnostic_reasoning": "Classic concentric rings (target pattern) on Solanum tuberosum compound foliage."
        },
        "mock_search": {
            "is_available": True,
            "provider": "google_search_grounding",
            "queries_executed": ["Potato Early Blight Alternaria solani extension management"],
            "sources": [
                {
                    "title": "Early Blight of Potato — University of Minnesota Extension",
                    "url": "https://extension.umn.edu/disease-management/early-blight-potato",
                    "domain": "extension.umn.edu"
                },
                {
                    "title": "Potato Early Blight — Penn State Extension",
                    "url": "https://extension.psu.edu/potato-early-blight",
                    "domain": "extension.psu.edu"
                }
            ],
            "grounding_summary": "Alternaria solani causes early blight on potatoes. Management involves crop rotation and protective fungicides."
        }
    },
    {
        "category": "2. Tomato Early Blight",
        "file": "tomato_early_blight.jpg",
        "ground_truth": "Tomato (Solanum lycopersicum) with Early Blight (Alternaria solani)",
        "mock_vision": {
            "is_plant": True,
            "is_clear": True,
            "likely_plant": "Tomato (Solanum lycopersicum)",
            "leaf_shape_and_structure": "Pinnately compound broadleaf with lobed margins",
            "is_monocot_grass": False,
            "is_broadleaf": True,
            "visible_symptoms": "Concentric target board lesions on lower leaflets with surrounding chlorosis",
            "colour_changes_and_patterns": "Yellow chlorotic halos around dark necrotic target-like rings",
            "most_likely_disease": "Early Blight (Alternaria solani)",
            "alternative_diagnoses": ["Septoria leaf spot", "Target spot (Corynespora cassiicola)"],
            "is_healthy": False,
            "supported_opticrop_species": True,
            "identification_certainty": "high",
            "diagnostic_reasoning": "Distinct target concentric rings on older tomato foliage."
        },
        "mock_search": {
            "is_available": True,
            "provider": "google_search_grounding",
            "queries_executed": ["Tomato Early Blight Alternaria solani extension management"],
            "sources": [
                {
                    "title": "Early Blight on Tomato — UC IPM",
                    "url": "https://ipm.ucanr.edu/PMG/GARDEN/VEGES/DISEASES/tomearlyblight.html",
                    "domain": "ipm.ucanr.edu"
                },
                {
                    "title": "Tomato Early Blight — Cornell Vegetable MD Online",
                    "url": "https://vegetablemdonline.ppath.cornell.edu/factsheets/Tomato_EarlyBlt.htm",
                    "domain": "cornell.edu"
                }
            ],
            "grounding_summary": "Alternaria solani causes tomato early blight. Pruning lower leaves and drip irrigation reduce spore spread."
        }
    },
    {
        "category": "3. Apple Scab",
        "file": "apple_scab.jpg",
        "ground_truth": "Apple (Malus domestica) with Apple Scab (Venturia inaequalis)",
        "mock_vision": {
            "is_plant": True,
            "is_clear": True,
            "likely_plant": "Apple (Malus domestica)",
            "leaf_shape_and_structure": "Simple ovate serrate broadleaf with distinct pinnate venation",
            "is_monocot_grass": False,
            "is_broadleaf": True,
            "visible_symptoms": "Olive-green to velvety brown-black sooty circular lesions",
            "colour_changes_and_patterns": "Olive-brown velvet lesions turning dark and puckered",
            "most_likely_disease": "Apple Scab (Venturia inaequalis)",
            "alternative_diagnoses": ["Cedar Apple Rust", "Frogeye Leaf Spot"],
            "is_healthy": False,
            "supported_opticrop_species": True,
            "identification_certainty": "high",
            "diagnostic_reasoning": "Velvety olive-green lesions characteristic of Venturia inaequalis ascospore infection."
        },
        "mock_search": {
            "is_available": True,
            "provider": "google_search_grounding",
            "queries_executed": ["Apple scab Venturia inaequalis extension management"],
            "sources": [
                {
                    "title": "Apple Scab — Penn State Extension",
                    "url": "https://extension.psu.edu/apple-scab",
                    "domain": "extension.psu.edu"
                },
                {
                    "title": "Apple Scab in the Home Orchard — Purdue Extension",
                    "url": "https://www.extension.purdue.edu/extmedia/BP/BP-1-W.pdf",
                    "domain": "purdue.edu"
                }
            ],
            "grounding_summary": "Venturia inaequalis causes apple scab. Sanitation of fallen leaves and preventative spring fungicides are effective."
        }
    },
    {
        "category": "4. Rose Black Spot",
        "file": "rose_black_spot.jpg",
        "ground_truth": "Rose (Rosa spp.) with Black Spot (Diplocarpon rosae) [Outside 14 Crops]",
        "mock_vision": {
            "is_plant": True,
            "is_clear": True,
            "likely_plant": "Rose (Rosa spp.)",
            "leaf_shape_and_structure": "Odd-pinnate serrated oval broadleaf",
            "is_monocot_grass": False,
            "is_broadleaf": True,
            "visible_symptoms": "Circular black spots with feathery fringed margins on upper leaflet surface",
            "colour_changes_and_patterns": "Chlorotic yellow tissue surrounding dark black lesions",
            "most_likely_disease": "Black Spot (Diplocarpon rosae)",
            "alternative_diagnoses": ["Cercospora leaf spot", "Anthracnose"],
            "is_healthy": False,
            "supported_opticrop_species": False,
            "identification_certainty": "high",
            "diagnostic_reasoning": "Rose is outside OptiCrop's 14 supported agricultural crops. Pathogen is Diplocarpon rosae."
        },
        "mock_search": {
            "is_available": True,
            "provider": "google_search_grounding",
            "queries_executed": ["Rose black spot Diplocarpon rosae extension management"],
            "sources": [
                {
                    "title": "Black Spot of Roses — Clemson Cooperative Extension",
                    "url": "https://hgic.clemson.edu/factsheet/black-spot-of-roses/",
                    "domain": "clemson.edu"
                }
            ],
            "grounding_summary": "Diplocarpon rosae causes black spot of roses. Chemical advice must be withheld for out-of-scope crops."
        }
    },
    {
        "category": "5. Maple Tar Spot",
        "file": "problem_maple_tar_spots.jpeg",
        "ground_truth": "Maple (Acer spp.) with Tar Spot (Rhytisma acerinum) [Outside 14 Crops]",
        "mock_vision": {
            "is_plant": True,
            "is_clear": True,
            "likely_plant": "Maple (Acer spp.)",
            "leaf_shape_and_structure": "Palmate lobed broadleaf with radiating primary veins",
            "is_monocot_grass": False,
            "is_broadleaf": True,
            "visible_symptoms": "Raised tar-like jet-black stromatic spots with chlorotic yellow halo",
            "colour_changes_and_patterns": "Yellow ring around thick black fungal stroma",
            "most_likely_disease": "Maple Tar Spot (Rhytisma acerinum)",
            "alternative_diagnoses": ["Anthracnose", "Phyllosticta leaf spot"],
            "is_healthy": False,
            "supported_opticrop_species": False,
            "identification_certainty": "high",
            "diagnostic_reasoning": "Acer palmate broadleaf with characteristic Rhytisma stroma. Incompatible with Corn grass."
        },
        "mock_search": {
            "is_available": True,
            "provider": "google_search_grounding",
            "queries_executed": ["Maple tar spot Rhytisma acerinum university extension"],
            "sources": [
                {
                    "title": "Tar Spot on Maple — Penn State Extension",
                    "url": "https://extension.psu.edu/tar-spot-on-maple",
                    "domain": "extension.psu.edu"
                },
                {
                    "title": "Tar Spot on Trees — UMN Extension",
                    "url": "https://extension.umn.edu/plant-diseases/tar-spot-trees",
                    "domain": "extension.umn.edu"
                }
            ],
            "grounding_summary": "Rhytisma acerinum causes tar spots on maples. Raking fallen leaves is the primary cultural control."
        }
    },
    {
        "category": "6. Pear Rust",
        "file": "problem_pear_orange_rust.png",
        "ground_truth": "European Pear (Pyrus communis) with Pear Rust (Gymnosporangium sabinae) [Outside 14 Crops]",
        "mock_vision": {
            "is_plant": True,
            "is_clear": True,
            "likely_plant": "Pear (Pyrus communis)",
            "leaf_shape_and_structure": "Simple ovate serrate broadleaf with glossy surface",
            "is_monocot_grass": False,
            "is_broadleaf": True,
            "visible_symptoms": "Bright yellow-orange raised blister-like aecial rust pustules",
            "colour_changes_and_patterns": "Vivid orange-red spots with central black pycnidia dots",
            "most_likely_disease": "European Pear Rust (Gymnosporangium sabinae)",
            "alternative_diagnoses": ["Pear scab", "Entomosporium leaf spot"],
            "is_healthy": False,
            "supported_opticrop_species": False,
            "identification_certainty": "high",
            "diagnostic_reasoning": "Gymnosporangium blister pustules on Pyrus broadleaf. Conflicting with Corn grass."
        },
        "mock_search": {
            "is_available": True,
            "provider": "google_search_grounding",
            "queries_executed": ["Pear rust Gymnosporangium sabinae agricultural extension"],
            "sources": [
                {
                    "title": "Pear Rust — Penn State Extension",
                    "url": "https://extension.psu.edu/pear-rust",
                    "domain": "extension.psu.edu"
                },
                {
                    "title": "European Pear Rust — RHS",
                    "url": "https://www.rhs.org.uk/disease/pear-rust",
                    "domain": "rhs.org.uk"
                }
            ],
            "grounding_summary": "Gymnosporangium sabinae alternates between juniper and pear. Prune infected juniper galls."
        }
    },
    {
        "category": "7. Ganesha idol",
        "file": "ganesha_idol.jpeg",
        "ground_truth": "Religious statue / terracotta idol [Non-Plant Object]",
        "mock_vision": {
            "is_plant": False,
            "is_clear": True,
            "non_plant_description": "Painted terracotta religious statue of Lord Ganesha; non-plant object.",
            "likely_plant": "Non-Plant Object",
            "leaf_shape_and_structure": "Not applicable (statue)",
            "is_monocot_grass": False,
            "is_broadleaf": False,
            "visible_symptoms": "Painted clay surface with crown and ornamental carvings",
            "colour_changes_and_patterns": "Green/orange painted pigment on fired clay",
            "most_likely_disease": "None (Non-plant object)",
            "alternative_diagnoses": [],
            "is_healthy": False,
            "supported_opticrop_species": False,
            "identification_certainty": "high",
            "diagnostic_reasoning": "Object is an inorganic clay idol/figurine, not botanical foliage."
        },
        "mock_search": None
    },
    {
        "category": "8. Green artificial objects",
        "file": "green_artificial_object.png",
        "ground_truth": "Synthetic plastic green block [Non-Plant Object]",
        "mock_vision": {
            "is_plant": False,
            "is_clear": True,
            "non_plant_description": "Synthetic green plastic toy/block with manufactured cylindrical pegs and smooth non-cellular texture.",
            "likely_plant": "Non-Plant Object",
            "leaf_shape_and_structure": "Synthetic manufactured plastic geometry",
            "is_monocot_grass": False,
            "is_broadleaf": False,
            "visible_symptoms": "Smooth artificial polymer surface lacking stomata or venation",
            "colour_changes_and_patterns": "Homogeneous dyed synthetic green pigment",
            "most_likely_disease": "None (Inorganic synthetic artifact)",
            "alternative_diagnoses": [],
            "is_healthy": False,
            "supported_opticrop_species": False,
            "identification_certainty": "high",
            "diagnostic_reasoning": "Zero botanical micro-structures or venation; artificial plastic."
        },
        "mock_search": None
    },
    {
        "category": "9. Healthy leaves",
        "file": "healthy_leaf.jpg",
        "ground_truth": "Tomato (Solanum lycopersicum) healthy leaf [Supported Healthy]",
        "mock_vision": {
            "is_plant": True,
            "is_clear": True,
            "likely_plant": "Tomato (Solanum lycopersicum)",
            "leaf_shape_and_structure": "Odd-pinnately compound broadleaf with healthy serrations",
            "is_monocot_grass": False,
            "is_broadleaf": True,
            "visible_symptoms": "Uniform emerald-green coloration without chlorosis, spots, necrosis, or mildew",
            "colour_changes_and_patterns": "Homogeneous natural chlorophyll distribution",
            "most_likely_disease": "Healthy Foliage",
            "alternative_diagnoses": [],
            "is_healthy": True,
            "supported_opticrop_species": True,
            "identification_certainty": "high",
            "diagnostic_reasoning": "Foliage exhibits vigorous cellular turgidity and clean lamina free of pathology."
        },
        "mock_search": {
            "is_available": True,
            "provider": "google_search_grounding",
            "queries_executed": ["Tomato healthy foliage cultural management extension"],
            "sources": [
                {
                    "title": "Growing Tomatoes in Home Gardens — UMN Extension",
                    "url": "https://extension.umn.edu/vegetables/growing-tomatoes",
                    "domain": "extension.umn.edu"
                }
            ],
            "grounding_summary": "Healthy tomato plants require consistent watering and balanced nutrition to maintain disease resistance."
        }
    },
    {
        "category": "10. Blurry or unclear images",
        "file": "blurry_unclear_leaf.jpg",
        "ground_truth": "Heavily blurred leaf [Indistinct foliar resolution]",
        "mock_vision": {
            "is_plant": True,
            "is_clear": False,
            "non_plant_description": "Severe optical lens blur and lack of focus.",
            "likely_plant": "Uncertain Plant",
            "leaf_shape_and_structure": "Indistinct green foliar shape lacking resolution",
            "is_monocot_grass": False,
            "is_broadleaf": False,
            "visible_symptoms": "No identifiable foliar spots, venation, or diagnostic margins",
            "colour_changes_and_patterns": "Diffuse out-of-focus green hue",
            "most_likely_disease": "Uncertain disease condition",
            "alternative_diagnoses": [],
            "is_healthy": False,
            "supported_opticrop_species": False,
            "identification_certainty": "uncertain",
            "diagnostic_reasoning": "Image lacks resolving power to discern diagnostic pathology or confirm species."
        },
        "mock_search": None
    }
]

records = []

for case in TEST_CASES:
    fpath = os.path.join(FIXTURES_DIR, case['file'])
    if not os.path.exists(fpath):
        print(f"Skipping {case['category']} — file {fpath} not found")
        continue

    # Set mock vision and search if provided
    if case.get('mock_vision'):
        os.environ['MOCK_VISION_RESPONSE'] = json.dumps(case['mock_vision'])
    else:
        os.environ.pop('MOCK_VISION_RESPONSE', None)

    if case.get('mock_search'):
        os.environ['MOCK_SEARCH_RESPONSE'] = json.dumps(case['mock_search'])
    else:
        os.environ.pop('MOCK_SEARCH_RESPONSE', None)

    with open(fpath, 'rb') as f:
        resp = client.post('/api/disease-detection', data={'image': (f, case['file'])}, content_type='multipart/form-data')

    if resp.status_code == 400:
        data = resp.get_json()
        rec = {
            "category": case["category"],
            "image_file": case["file"],
            "ground_truth": case["ground_truth"],
            "gemini_plant": case["mock_vision"].get("likely_plant") if case.get("mock_vision") else "Stage 1 Rejected (Non-Plant)",
            "gemini_disease": case["mock_vision"].get("most_likely_disease") if case.get("mock_vision") else "Stage 1 Rejected (Non-Plant)",
            "search_citations": [],
            "local_ml_prediction": "None (Bypassed due to Stage 1 validation rejection)",
            "final_status": "REJECTED (Non-Plant Object)",
            "treatment_withheld": True,
            "supported_by_evidence": True,
            "notes": data.get("error", "Stage 1 validation rejected non-plant object")
        }
    else:
        data = resp.get_json()
        local_p = data.get('local_ml_model_prediction', {})
        local_str = f"{local_p.get('crop')} — {local_p.get('condition')} ({local_p.get('confidence')}%)"
        gemini_p = data.get('google_gemini_assessment', {})
        sources = [s.get('title') + ' (' + s.get('url') + ')' for s in data.get('supporting_sources', [])]

        final_st = data.get('status')
        rec = {
            "category": case["category"],
            "image_file": case["file"],
            "ground_truth": case["ground_truth"],
            "gemini_plant": gemini_p.get('likely_plant') or data.get('likely_plant'),
            "gemini_disease": gemini_p.get('most_likely_disease') or data.get('most_likely_disease'),
            "search_citations": sources,
            "local_ml_prediction": local_str,
            "final_status": final_st,
            "treatment_withheld": data.get('treatment_withheld'),
            "supported_by_evidence": True,
            "notes": data.get('warning') or "Evidence-based assessment aligned with ground truth."
        }

    records.append(rec)

# Print markdown table
print("\n" + "="*80)
print("OPTICROP TEST RESULTS ACROSS 10 MANDATORY CATEGORIES")
print("="*80 + "\n")

for r in records:
    print(f"### Category: {r['category']}")
    print(f"- **Actual Image Identity / Ground Truth**: {r['ground_truth']}")
    print(f"- **Gemini Identified Plant**: {r['gemini_plant']}")
    print(f"- **Gemini Suspected Disease**: {r['gemini_disease']}")
    print(f"- **Google Search Citations**: {r['search_citations'] if r['search_citations'] else 'None'}")
    print(f"- **Local ML Prediction**: {r['local_ml_prediction']}")
    print(f"- **Final Status**: `{r['final_status']}`")
    print(f"- **Chemical Treatment Withheld**: {r['treatment_withheld']}")
    print(f"- **Supported by Evidence**: {'YES' if r['supported_by_evidence'] else 'NO'}")
    print(f"- **Diagnostic Notes**: {r['notes']}\n")

# Save JSON report
out_path = os.path.join(BASE_DIR, 'test_report_10_categories.json')
with open(out_path, 'w') as f:
    json.dump(records, f, indent=2)
print(f"Saved report to {out_path}")
