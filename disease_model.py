import os
import io
import json
import urllib.request
import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_WEIGHTS_PATH = os.environ.get("MODEL_WEIGHTS_PATH", os.path.join(BASE_DIR, "plant_disease_mobilenet_v2.pth"))
TRAINED_MODEL_PATH = os.environ.get("TRAINED_MODEL_PATH", os.path.join(BASE_DIR, "training_output", "best_model.pth"))
TRAINED_CLASS_MAP = os.environ.get("TRAINED_CLASS_MAP", os.path.join(BASE_DIR, "class_mapping.json") if os.path.exists(os.path.join(BASE_DIR, "class_mapping.json")) else os.path.join(BASE_DIR, "training_output", "class_mapping.json"))
ONNX_MODEL_PATH = os.environ.get("ONNX_MODEL_PATH", os.environ.get("DISEASE_MODEL_PATH", os.path.join(BASE_DIR, "plant_disease_model.onnx")))

# Benchmark PlantVillage 38 Classes (standard pathology labels)
CLASS_NAMES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]

# Agronomic knowledge base for symptoms, biology, and cautious cultural care
DISEASE_METADATA = {
    'Apple___Apple_scab': {
        'crop': 'Apple',
        'condition': 'Apple Scab (Venturia inaequalis)',
        'is_healthy': False,
        'severity': 'Moderate to High',
        'symptoms': 'Olive-green to velvety dark brown lesions on the upper leaf surface, later turning black and corky with premature leaf drop.',
        'care': [
            'Rake and dispose of fallen infected leaves in autumn to disrupt the primary fungal overwintering cycle.',
            'Prune tree canopies during the dormant season to maximize internal sunlight penetration and speed leaf drying.',
            'Apply preventive bio-fungicides (e.g. sulfur or copper octanoate) during early bud break before rainy periods.'
        ],
        'prevention': 'Select scab-resistant apple cultivars (e.g., Liberty, Enterprise, Freedom) for humid growing zones.'
    },
    'Apple___Black_rot': {
        'crop': 'Apple',
        'condition': 'Black Rot (Botryosphaeria obtusa)',
        'is_healthy': False,
        'severity': 'High',
        'symptoms': 'Circular purple-bordered leaf spots (frogeye leaf spot), progressing to necrotic lesions and sunken black cankers on woody twigs.',
        'care': [
            'Prune out dead wood, cankered limbs, and mummified fruit at least 15 cm below infected tissue.',
            'Sanitize pruning tools with 70% isopropyl alcohol between cuts to prevent pathogen transmission.',
            'Apply captan or thiophanate-methyl sprays starting from petal fall where disease pressure is historical.'
        ],
        'prevention': 'Maintain tree vigor with balanced nitrogen feeding; avoid excessive fertilizer that encourages overly lush tender shoots.'
    },
    'Apple___Cedar_apple_rust': {
        'crop': 'Apple',
        'condition': 'Cedar Apple Rust (Gymnosporangium juniperi-virginianae)',
        'is_healthy': False,
        'severity': 'Moderate',
        'symptoms': 'Bright yellow-orange or reddish spots on the upper leaf surface with tiny black fruiting bodies in the center.',
        'care': [
            'Remove nearby wild juniper or eastern red cedar galls within 300 meters if feasible to break the heteroecious cycle.',
            'Apply protective fungicides from tight cluster through petal fall when cedar galls produce gelatinous orange horns.',
            'Avoid overhead sprinklers that keep foliage wet during warm morning hours.'
        ],
        'prevention': 'Plant rust-immune varieties such as Redfree, Priscilla, or William’s Pride.'
    },
    'Apple___healthy': {
        'crop': 'Apple',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Leaves exhibit uniform deep green coloration, firm turgor, intact margins, and no visible necrotic or chlorotic lesions.',
        'care': [
            'Continue standard orchard management: maintain soil moisture balance and monitor seasonal nutrient needs.',
            'Inspect weekly for early aphid, mite, or powdery mildew occurrences.',
            'Ensure adequate mulch around the tree drip line to maintain root moisture.'
        ],
        'prevention': 'Maintain balanced pruning and balanced soil organic matter.'
    },
    'Blueberry___healthy': {
        'crop': 'Blueberry',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Vibrant, waxy green leaves with no spotting, chlorosis, or twig dieback.',
        'care': [
            'Maintain acidic soil conditions (optimal pH 4.5 - 5.5) using elemental sulfur or peat moss.',
            'Irrigate regularly with clean, low-salinity water to support shallow root systems.'
        ],
        'prevention': 'Mulch with pine needles or wood chips to suppress weed competition.'
    },
    'Cherry_(including_sour)___Powdery_mildew': {
        'crop': 'Cherry',
        'condition': 'Powdery Mildew (Podosphaera clandestina)',
        'is_healthy': False,
        'severity': 'Moderate',
        'symptoms': 'White powdery fungal patches on young foliage and shoots, causing leaf distortion, upward curling, and premature yellowing.',
        'care': [
            'Prune dense water sprouts in the center of the tree to increase cross-canopy air circulation.',
            'Apply horticultural oils, potassium bicarbonate, or sulfur sprays at the first sign of powdery patches.',
            'Avoid evening overhead sprinkler irrigation.'
        ],
        'prevention': 'Avoid excessive spring nitrogen fertilization that stimulates overly succulent terminal growth.'
    },
    'Cherry_(including_sour)___healthy': {
        'crop': 'Cherry',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Glossy, uniformly green leaves with clean petioles and active apical terminal growth.',
        'care': [
            'Maintain regular irrigation schedules and monitor for cherry fruit flies and mites.',
            'Ensure proper post-harvest nitrogen management.'
        ],
        'prevention': 'Keep orchard floor clean of diseased leaf litter.'
    },
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': {
        'crop': 'Corn (Maize)',
        'condition': 'Gray Leaf Spot (Cercospora zeae-maydis)',
        'is_healthy': False,
        'severity': 'High',
        'symptoms': 'Narrow, rectangular, tan-to-gray lesions restricted by leaf veins running parallel to the leaf margin.',
        'care': [
            'Implement 1 to 2-year crop rotation with non-host crops (soybean, sunflower, or cotton) to deplete field inoculum.',
            'Utilize minimum or conservation tillage to bury crop residue where severe infestations occur.',
            'Apply foliar fungicides (strobilurins or triazoles) at VT (tasseling) stage if lesions appear below the ear leaf.'
        ],
        'prevention': 'Plant corn hybrids with proven genetic resistance and manage plant population density.'
    },
    'Corn_(maize)___Common_rust_': {
        'crop': 'Corn (Maize)',
        'condition': 'Common Rust (Puccinia sorghi)',
        'is_healthy': False,
        'severity': 'Moderate',
        'symptoms': 'Oval to elongate golden-brown to dark cinnamon pustules (uredinia) scattered across both upper and lower leaf surfaces.',
        'care': [
            'Fungicide application is typically only justified on seed corn or susceptible sweet corn if pustules appear before blister stage.',
            'Maintain balanced soil potassium levels, which help plants tolerate rust infection.',
            'Scout fields frequently during cool (16-25°C), high-humidity weather.'
        ],
        'prevention': 'Plant hybrids possessing Rp-resistant genes.'
    },
    'Corn_(maize)___Northern_Leaf_Blight': {
        'crop': 'Corn (Maize)',
        'condition': 'Northern Corn Leaf Blight (Exserohilum turcicum)',
        'is_healthy': False,
        'severity': 'High',
        'symptoms': 'Long, elliptical, cigar-shaped grayish-green to tan lesions (2.5 to 15 cm long) on foliage.',
        'care': [
            'Rotate away from corn for at least one season to allow corn residue decomposition.',
            'Apply fungicides if weather is wet and lesions are present on or near the ear leaf before pollination.',
            'Shred or deep-till residue in heavily infested fields post-harvest.'
        ],
        'prevention': 'Utilize NCLB-resistant seed hybrids with multi-gene background resistance.'
    },
    'Corn_(maize)___healthy': {
        'crop': 'Corn (Maize)',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Robust, broad green leaves with active photosynthetic vigor and uniform vein structure.',
        'care': [
            'Maintain side-dress nitrogen fertilization according to growth stage (V4 - V8).',
            'Ensure adequate soil moisture during silking and grain filling.'
        ],
        'prevention': 'Maintain weed-free field borders to minimize insect vectors.'
    },
    'Grape___Black_rot': {
        'crop': 'Grape',
        'condition': 'Black Rot (Guignardia bidwellii)',
        'is_healthy': False,
        'severity': 'High',
        'symptoms': 'Small reddish-brown circular spots on foliage with dark margins, developing tiny black pimple-like pycnidia.',
        'care': [
            'Remove and destroy all mummified berries from vines and vineyard floor during winter dormancy.',
            'Canopy management: shoot-thinning and leaf-pulling around grape clusters to maximize rapid drying.',
            'Spray protectant fungicides (mancozeb, ziram, or myclobutanil) from early shoot growth through fruit set.'
        ],
        'prevention': 'Orient vine rows parallel to prevailing winds to encourage airflow.'
    },
    'Grape___Esca_(Black_Measles)': {
        'crop': 'Grape',
        'condition': 'Esca / Black Measles (Phaeomoniella / Phaeoacremonium)',
        'is_healthy': False,
        'severity': 'Critical',
        'symptoms': 'Interveinal necrosis causing a distinctive "tiger-stripe" pattern of yellow/red and brown areas between green veins.',
        'care': [
            'Mark affected vines and perform remedial surgery (trunk renewal) by cutting below symptomatic vascular tissue.',
            'Protect pruning wounds with wound sealants or Trichoderma-based biological protectors within 24 hours of cutting.',
            'Avoid pruning during wet periods when fungal airborne spores are actively released.'
        ],
        'prevention': 'Prune late in the dormant season (double pruning) to allow wounds to heal more rapidly in spring.'
    },
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': {
        'crop': 'Grape',
        'condition': 'Isariopsis Leaf Spot (Pseudocercospora cladosporioides)',
        'is_healthy': False,
        'severity': 'Moderate',
        'symptoms': 'Irregular brown lesions on leaves, often with faint chlorotic halos, causing premature leaf browning in late summer.',
        'care': [
            'Improve canopy ventilation by trimming excessive lateral canes and removing dense leaves around the fruit zone.',
            'Apply protective copper-based sprays or triazole fungicides during post-bloom periods.'
        ],
        'prevention': 'Maintain clean vineyard floor and remove infected leaf litter post-harvest.'
    },
    'Grape___healthy': {
        'crop': 'Grape',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Broad, well-formed green leaves free of spots, necrosis, or curl, supporting vigorous tendrils and clusters.',
        'care': [
            'Maintain shoot positioning and regular irrigation according to phenological stage.',
            'Monitor for spider mites, phylloxera, and downy mildew during humid weather.'
        ],
        'prevention': 'Keep trellis clean and maintain balanced vine crop loads.'
    },
    'Orange___Haunglongbing_(Citrus_greening)': {
        'crop': 'Orange (Citrus)',
        'condition': 'Citrus Greening / Huanglongbing (Candidatus Liberibacter)',
        'is_healthy': False,
        'severity': 'Critical',
        'symptoms': 'Asymmetrical yellow blotchy mottle on leaves crossing vein boundaries, yellow shoot dieback, and small lopsided bitter fruit.',
        'care': [
            'Quarantine and control the Asian Citrus Psyllid (Diaphorina citri) vector using targeted insecticides and systemic treatments.',
            'Promptly remove and destroy confirmed infected trees to protect surrounding groves.',
            'Supply supplemental foliar micronutrients (zinc, iron, manganese) to sustain tree health temporarily.'
        ],
        'prevention': 'Source only certified disease-free budwood from certified clean nursery stock.'
    },
    'Peach___Bacterial_spot': {
        'crop': 'Peach',
        'condition': 'Bacterial Spot (Xanthomonas arboricola pv. pruni)',
        'is_healthy': False,
        'severity': 'High',
        'symptoms': 'Angular, water-soaked dark purple to black spots on leaves, often dropping out to give a "shot-hole" appearance.',
        'care': [
            'Apply dormant copper sprays before bud swell and low-rate oxytetracycline or copper sprays during bloom in wet springs.',
            'Avoid excessive nitrogen fertilization which creates tender tissue vulnerable to bacterial entry.',
            'Avoid overhead sprinkler irrigation.'
        ],
        'prevention': 'Plant windbreaks in sandy locations to reduce windblown sand abrasions that provide bacterial entry points.'
    },
    'Peach___healthy': {
        'crop': 'Peach',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Smooth, elongated lanceolate leaves with glossy green lamina and no chlorosis or shot-hole lesions.',
        'care': [
            'Ensure adequate irrigation during fruit sizing and maintain post-harvest potassium levels.',
            'Monitor for peach tree borer and brown rot.'
        ],
        'prevention': 'Maintain open-center tree training for sunlight penetration.'
    },
    'Pepper,_bell___Bacterial_spot': {
        'crop': 'Bell Pepper',
        'condition': 'Bacterial Spot (Xanthomonas campestris pv. vesicatoria)',
        'is_healthy': False,
        'severity': 'High',
        'symptoms': 'Small, water-soaked, dark-brown circular to irregular spots on leaves, becoming necrotic and causing severe defoliation.',
        'care': [
            'Rotate pepper and tomato plantings with non-solanaceous crops for at least 2 to 3 years.',
            'Avoid working in fields when foliage is wet from rain or dew to prevent physical spread.',
            'Apply preventive fixed copper combined with mancozeb or bio-fungicide Bacillus subtilis sprays.'
        ],
        'prevention': 'Use certified pathogen-free seeds treated with hot water (50°C for 25 min) or sodium hypochlorite.'
    },
    'Pepper,_bell___healthy': {
        'crop': 'Bell Pepper',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Uniformly green, smooth leaves with intact margins, vigorous branching, and healthy blossom nodes.',
        'care': [
            'Maintain steady drip irrigation to prevent blossom end rot and calcium deficiency.',
            'Provide balanced N-P-K fertilizer with adequate magnesium.'
        ],
        'prevention': 'Mulch plastic beds to prevent soil splash onto foliage.'
    },
    'Potato___Early_blight': {
        'crop': 'Potato',
        'condition': 'Early Blight (Alternaria solani)',
        'is_healthy': False,
        'severity': 'Moderate to High',
        'symptoms': 'Dark brown to black lesions showing distinctive concentric rings (target pattern), primarily on older lower foliage with chlorotic yellow halos.',
        'care': [
            'Maintain robust vine health: early blight aggressively targets stressed, nitrogen-depleted, or senescent plants.',
            'Avoid sprinkler irrigation late in the afternoon so foliage dries quickly before nightfall.',
            'Apply protective fungicides (chlorothalonil, mancozeb, or azoxystrobin) upon detecting first lower leaf lesions.'
        ],
        'prevention': 'Practice 3-year crop rotation and eradicate volunteer potato plants and solanaceous weeds (nightshade).'
    },
    'Potato___Late_blight': {
        'crop': 'Potato',
        'condition': 'Late Blight (Phytophthora infestans)',
        'is_healthy': False,
        'severity': 'Critical',
        'symptoms': 'Large, irregular, water-soaked lesions that rapidly expand and turn purplish-black, with delicate white fungal-like sporulation on leaf undersides in high humidity.',
        'care': [
            'Immediate action required: late blight can destroy entire fields within days under cool, humid weather.',
            'Apply systemic fungicides (mefenoxam, cymoxanil, or fluopicolide) according to local blight forecasting warnings.',
            'Destroy and haul away infected cull piles and destroy infected foliage before harvest to prevent tuber infection.'
        ],
        'prevention': 'Plant certified disease-free seed tubers and select resistant varieties where available.'
    },
    'Potato___healthy': {
        'crop': 'Potato',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Dark green compound leaves with firm leaflets, active stolon and canopy expansion, and clean petioles.',
        'care': [
            'Maintain steady soil hilling to protect developing tubers from sunlight and blight spores.',
            'Ensure adequate irrigation during tuber initiation.'
        ],
        'prevention': 'Regular scouting during periods of cool, wet weather.'
    },
    'Raspberry___healthy': {
        'crop': 'Raspberry',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Serrate, bright green leaflets with pale undersides and vigorous primocane growth.',
        'care': [
            'Trellis canes to maintain upright growth and weed control.',
            'Provide consistent drip watering to root zones.'
        ],
        'prevention': 'Prune spent floricanes after fruiting to improve airflow.'
    },
    'Soybean___healthy': {
        'crop': 'Soybean',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Trifoliate leaves exhibiting uniform green coloration, active nodulation, and healthy trifoliate emergence.',
        'care': [
            'Monitor for aphids, stink bugs, and defoliating caterpillars during pod filling.',
            'Ensure adequate soil phosphorus and potassium.'
        ],
        'prevention': 'Rotate annually with corn or wheat to manage soil-borne nematodes.'
    },
    'Squash___Powdery_mildew': {
        'crop': 'Squash',
        'condition': 'Powdery Mildew (Podosphaera xanthii)',
        'is_healthy': False,
        'severity': 'Moderate',
        'symptoms': 'Talcum powder-like white fungal colonies on upper and lower leaf surfaces, causing leaves to become chlorotic, brown, and brittle.',
        'care': [
            'Plant in full sunlight with generous plant spacing to allow continuous air passage through the canopy.',
            'Apply potassium bicarbonate, neem oil, or horticultural oils early in the disease progression.',
            'Remove heavily infected older leaves at the base of the plant to reduce inoculum pressure.'
        ],
        'prevention': 'Select powdery mildew-resistant squash and pumpkin hybrids.'
    },
    'Strawberry___Leaf_scorch': {
        'crop': 'Strawberry',
        'condition': 'Leaf Scorch (Diplocarpon earlianum)',
        'is_healthy': False,
        'severity': 'Moderate',
        'symptoms': 'Numerous small, dark purple or reddish spots on upper leaf surfaces that enlarge and coalesce, giving the foliage a scorched, burned appearance.',
        'care': [
            'Renovate strawberry beds after harvest: mow, narrow rows, and rake away old infected foliage.',
            'Ensure adequate plant spacing to allow leaves to dry rapidly following rain or overhead watering.',
            'Apply protective fungicides (captan or pyraclostrobin) if scorch was severe the previous season.'
        ],
        'prevention': 'Use drip irrigation beneath plastic mulch instead of overhead sprinklers.'
    },
    'Strawberry___healthy': {
        'crop': 'Strawberry',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Trifoliate leaves with vivid green pigmentation, serrated margins, clean crowns, and vigorous runner formation.',
        'care': [
            'Maintain straw mulching to keep berries and lower foliage off bare soil.',
            'Provide balanced fertilizer following fruiting renovation.'
        ],
        'prevention': 'Plant on raised beds to ensure rapid water drainage.'
    },
    'Tomato___Bacterial_spot': {
        'crop': 'Tomato',
        'condition': 'Bacterial Spot (Xanthomonas perforans / euvesicatoria)',
        'is_healthy': False,
        'severity': 'High',
        'symptoms': 'Small (1-3 mm), dark, water-soaked circular to angular spots with yellow halos, leading to severe leaf blight and fruit spotting.',
        'care': [
            'Do not cultivate, tie, or harvest plants while foliage is wet from rain or morning dew.',
            'Apply fixed copper combined with mancozeb or bacteriophage products to suppress bacterial spread.',
            'Disinfect stakes, trellis wires, and pruning equipment with 10% bleach or sanitizing quaternary solution.'
        ],
        'prevention': 'Plant certified disease-free seeds and seedlings; rotate fields out of solanaceous crops for 2+ years.'
    },
    'Tomato___Early_blight': {
        'crop': 'Tomato',
        'condition': 'Early Blight (Alternaria solani)',
        'is_healthy': False,
        'severity': 'Moderate to High',
        'symptoms': 'Brown to black lesions with characteristic concentric rings (target pattern) on older lower leaves, surrounded by a prominent chlorotic yellow zone.',
        'care': [
            'Prune and destroy infected lower leaves up to the first flowering cluster to remove disease reservoir.',
            'Mulch around the base of plants with straw or plastic to prevent rain splash of fungal spores from soil.',
            'Apply chlorothalonil, copper fungicide, or Bacillus amyloliquefaciens preventive sprays.'
        ],
        'prevention': 'Space plants 45-60 cm apart, stake or cage vines, and water exclusively at the base with drip lines.'
    },
    'Tomato___Late_blight': {
        'crop': 'Tomato',
        'condition': 'Late Blight (Phytophthora infestans)',
        'is_healthy': False,
        'severity': 'Critical',
        'symptoms': 'Rapidly expanding water-soaked dark greenish-brown lesions that turn dark brown and papery, often accompanied by white fluffy mold on leaf undersides in humid conditions.',
        'care': [
            'High urgency: late blight destroys vines and fruit in cool (10-22°C), wet weather within 7-10 days.',
            'Immediately isolate infected plants; remove severely damaged plants in plastic bags to avoid airborne spore dispersal.',
            'Apply targeted fungicides (chlorothalonil, mancozeb, or cymoxanil) immediately upon disease appearance in the region.'
        ],
        'prevention': 'Avoid planting adjacent to potato fields; choose late blight-resistant varieties (e.g., Mountain Magic, Defiant).'
    },
    'Tomato___Leaf_Mold': {
        'crop': 'Tomato',
        'condition': 'Leaf Mold (Passalora fulva / Cladosporium fulvum)',
        'is_healthy': False,
        'severity': 'Moderate',
        'symptoms': 'Pale yellow chlorotic patches on the upper leaf surface matching olive-green to brownish velvety fungal growth on the underside.',
        'care': [
            'Common in high tunnels and greenhouses: aggressively ventilate and lower relative humidity below 85%.',
            'Increase plant spacing and prune lower suckers to optimize cross-canopy airflow.',
            'Apply copper or biological fungicides early if environmental humidity cannot be reduced.'
        ],
        'prevention': 'Plant greenhouse varieties bred with specific Cf resistance genes.'
    },
    'Tomato___Septoria_leaf_spot': {
        'crop': 'Tomato',
        'condition': 'Septoria Leaf Spot (Septoria lycopersici)',
        'is_healthy': False,
        'severity': 'High',
        'symptoms': 'Numerous small (1.5 - 3 mm) circular spots with grayish-white centers, dark brown margins, and minute black specks (pycnidia) inside the lesions.',
        'care': [
            'Pick off and destroy infected lower leaves as soon as first spots emerge at ground level.',
            'Apply thick mulch (wood chips, straw) to prevent soil-splash from splashing overwintered spores onto lower leaves.',
            'Spray with protective fungicides (copper or chlorothalonil) on a 7 to 10-day schedule during rainy weather.'
        ],
        'prevention': 'Thoroughly destroy or till in all tomato crop debris at the conclusion of the season.'
    },
    'Tomato___Spider_mites Two-spotted_spider_mite': {
        'crop': 'Tomato',
        'condition': 'Two-Spotted Spider Mite (Tetranychus urticae)',
        'is_healthy': False,
        'severity': 'Moderate',
        'symptoms': 'Fine yellow-white stippling (pinpoint dots) on the upper leaf surface, progressing to bronzing, leaf desiccation, and fine silken webbing on leaf undersides.',
        'care': [
            'Spray plants with strong water jets to physically dislodge mites and disrupt web colonies.',
            'Apply insecticidal soaps, neem oil, or horticultural oils thoroughly coating leaf undersides.',
            'Release predatory mites (Phytoseiulus persimilis) in enclosed greenhouses or high tunnels.'
        ],
        'prevention': 'Avoid over-fertilizing with nitrogen, which increases mite reproductive rates; manage dust along farm roads.'
    },
    'Tomato___Target_Spot': {
        'crop': 'Tomato',
        'condition': 'Target Spot (Corynespora cassiicola)',
        'is_healthy': False,
        'severity': 'Moderate to High',
        'symptoms': 'Small, pinpoint water-soaked lesions that enlarge into circular brown lesions with light brown centers and faint target-like concentric rings.',
        'care': [
            'Maintain plant pruning to ensure air circulation within the canopy.',
            'Avoid overhead irrigation that extends leaf wetness periods beyond 6 hours.',
            'Apply registered fungicides (azoxystrobin, difenoconazole, or copper compounds) at early canopy closure.'
        ],
        'prevention': 'Rotate with non-host crops and eliminate weed hosts in field perimeters.'
    },
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
        'crop': 'Tomato',
        'condition': 'Tomato Yellow Leaf Curl Virus (TYLCV)',
        'is_healthy': False,
        'severity': 'Critical',
        'symptoms': 'Marked upward cupping and curling of leaflet margins, prominent marginal chlorosis (yellowing), severely stunted plants, and arrested flower development.',
        'care': [
            'TYLCV is vectored by sweetpotato whiteflies (Bemisia tabaci): control whitefly populations using insecticidal soaps or systemic treatments.',
            'Infected plants cannot be cured: promptly rogue out and bag infected plants to prevent vectors from spreading virus to healthy rows.',
            'Use yellow sticky cards to monitor whitefly influx into fields and tunnels.'
        ],
        'prevention': 'Install fine insect-proof mesh (50-mesh) on greenhouse vents; plant resistant hybrids (e.g., Tygress, Red Bounty).'
    },
    'Tomato___Tomato_mosaic_virus': {
        'crop': 'Tomato',
        'condition': 'Tomato Mosaic Virus (ToMV)',
        'is_healthy': False,
        'severity': 'High',
        'symptoms': 'Mottled light and dark green mosaic patterns on leaves, leaf distortion (shoestring effect or fern-like leaves), and stunted vigor.',
        'care': [
            'ToMV is mechanically transmitted via hands, tools, and clothing: disinfect tools frequently with 20% non-fat dry milk solution or 10% bleach.',
            'Workers should wash hands thoroughly with soap before handling plants; smokers must avoid touching plants due to related tobacco virus transmission.',
            'Remove and incinerate infected plants immediately.'
        ],
        'prevention': 'Select seed certified tested for ToMV and plant resistant cultivars (marked with "T" or "ToMV").'
    },
    'Tomato___healthy': {
        'crop': 'Tomato',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'severity': 'None',
        'symptoms': 'Deep green composite leaves with robust turgidity, clean margins, strong stem development, and productive blossom clusters.',
        'care': [
            'Maintain consistent drip irrigation to avoid blossom-end rot and fruit cracking.',
            'Prune indeterminate vines according to trellis configuration to balance leaf area and fruit load.'
        ],
        'prevention': 'Mulch root zone, maintain consistent calcium levels, and scout weekly.'
    }
}

class PlantDiseaseDetector:
    _instance = None
    
    def __init__(self):
        self.session = None  # ONNX Runtime session
        self.model = None    # PyTorch model (fallback)
        self.device = None
        self.use_onnx = False
        self._initialize_pipeline()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PlantDiseaseDetector()
        return cls._instance

    def _initialize_pipeline(self):
        """Initialize model — prefer ONNX Runtime, fall back to PyTorch."""
        onnx_path = ONNX_MODEL_PATH

        # If ONNX model does not exist locally, attempt downloading from remote URL if configured
        if not os.path.exists(onnx_path):
            remote_url = os.environ.get("ONNX_MODEL_URL") or os.environ.get("DISEASE_MODEL_URL")
            if remote_url:
                try:
                    import tempfile
                    target_dir = os.environ.get("VERCEL_TMPDIR", tempfile.gettempdir())
                    target_file = os.path.join(target_dir, "plant_disease_model.onnx")
                    if not os.path.exists(target_file) or os.path.getsize(target_file) < 1024 * 1024:
                        print(f"Downloading disease model weights from {remote_url} to {target_file}...")
                        req = urllib.request.Request(remote_url, headers={'User-Agent': 'OptiCrop/1.0'})
                        with urllib.request.urlopen(req, timeout=45) as resp, open(target_file, 'wb') as out_f:
                            while True:
                                chunk = resp.read(65536)
                                if not chunk:
                                    break
                                out_f.write(chunk)
                        print(f"Disease model downloaded successfully ({os.path.getsize(target_file)} bytes).")
                    if os.path.exists(target_file) and os.path.getsize(target_file) > 1024 * 1024:
                        onnx_path = target_file
                except Exception as dl_err:
                    print(f"Failed to download remote disease model: {dl_err}")

        # Try ONNX Runtime first (lightweight, Vercel-compatible)
        if os.path.exists(onnx_path):
            try:
                import onnxruntime as ort
                self.session = ort.InferenceSession(
                    onnx_path,
                    providers=['CPUExecutionProvider']
                )
                # Verify model with warm-up inference to guarantee correct output shape
                dummy_input = np.zeros((1, 3, 224, 224), dtype=np.float32)
                in_name = self.session.get_inputs()[0].name
                warmup_out = self.session.run(None, {in_name: dummy_input})[0]
                if warmup_out.shape[-1] != len(CLASS_NAMES):
                    raise ValueError(f"Model output dimension mismatch: expected {len(CLASS_NAMES)}, got {warmup_out.shape[-1]}")
                self.use_onnx = True
                self.model = True  # Sentinel for health checks
                print(f"Plant Disease Detector initialized with ONNX Runtime ({onnx_path})!")
                return
            except Exception as e:
                print(f"ONNX Runtime init failed: {e}, falling back to PyTorch...")

        # Fallback: PyTorch
        try:
            import torch
            import torch.nn as nn
            from torchvision import models, transforms

            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            print(f"Initializing Plant Disease Detector on device: {self.device}")

            self.model = models.mobilenet_v2(weights=None)
            in_features = self.model.classifier[1].in_features
            self.model.classifier = nn.Sequential(
                nn.Dropout(p=0.3),
                nn.Linear(in_features, len(CLASS_NAMES))
            )

            # Priority: 1) Our trained model, 2) Legacy third-party weights
            loaded = False
            if os.path.exists(TRAINED_MODEL_PATH):
                try:
                    print(f"Loading OptiCrop-trained model from {TRAINED_MODEL_PATH}...")
                    checkpoint = torch.load(TRAINED_MODEL_PATH, map_location=self.device)
                    # Load class mapping from checkpoint if available
                    if 'class_mapping' in checkpoint:
                        trained_classes = checkpoint['class_mapping']
                        print(f"  Trained on {checkpoint.get('num_classes', len(trained_classes))} classes, "
                              f"best val_acc={checkpoint.get('val_acc', 'N/A'):.2f}%")
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                    loaded = True
                    print("OptiCrop-trained disease model loaded successfully!")
                except Exception as e:
                    print(f"Failed to load trained model: {e}, trying legacy weights...")

            if not loaded and os.path.exists(MODEL_WEIGHTS_PATH):
                print(f"Loading legacy fine-tuned weights from {MODEL_WEIGHTS_PATH}...")
                state_dict = torch.load(MODEL_WEIGHTS_PATH, map_location=self.device)
                remap = {}
                for k, v in state_dict.items():
                    new_k = k
                    if k == 'classifier.1.1.weight':
                        new_k = 'classifier.1.weight'
                    elif k == 'classifier.1.1.bias':
                        new_k = 'classifier.1.bias'
                    remap[new_k] = v
                self.model.load_state_dict(remap, strict=False)
                loaded = True

            if not loaded:
                print("Warning: No disease model weights found. Using untrained model.")

            self.model.to(self.device)
            self.model.eval()

            self._torch_transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            self.use_onnx = False
            print("Plant Disease Detector initialized with PyTorch!")
        except Exception as e:
            print(f"Warning: Could not initialize deep learning pipeline: {e}")
            self.model = None

    def _preprocess_image_numpy(self, image):
        """Preprocess PIL Image to numpy array for ONNX Runtime (no PyTorch needed)."""
        image = image.convert('RGB').resize((224, 224), Image.BILINEAR)
        img_array = np.array(image, dtype=np.float32) / 255.0
        # Normalize with ImageNet mean/std
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        img_array = (img_array - mean) / std
        # HWC -> CHW -> NCHW
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

    def _softmax(self, logits):
        """Compute softmax over a 1-D numpy array."""
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / exp_logits.sum()

    def _entropy(self, probs):
        """Compute Shannon entropy of probability distribution. Higher = more uncertain."""
        probs = probs[probs > 1e-10]  # avoid log(0)
        return -np.sum(probs * np.log(probs))

    def _max_entropy(self, n_classes):
        """Maximum possible entropy for n_classes (uniform distribution)."""
        return np.log(n_classes)

    def predict(self, image_bytes):
        """
        Runs real-time inference on an input image byte stream.
        Returns structured prediction diagnostics, symptoms, care advice, and confidence calibrations.
        """
        if self.model is None:
            return {
                'success': False,
                'error': 'Deep Learning inference engine is not ready. Model unavailable.'
            }

        try:
            # 1. Open and validate image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

            if self.use_onnx and self.session is not None:
                # ONNX Runtime inference
                input_array = self._preprocess_image_numpy(image)
                input_name = self.session.get_inputs()[0].name
                logits = self.session.run(None, {input_name: input_array})[0][0]
                probs = self._softmax(logits)
                top_indices = np.argsort(probs)[::-1][:3]
                top_probs = probs[top_indices]
            else:
                # PyTorch inference
                import torch
                import torch.nn.functional as F
                tensor = self._torch_transform(image).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    logits = self.model(tensor)
                    probs_t = F.softmax(logits, dim=1)[0]
                top_probs_t, top_indices_t = torch.topk(probs_t, k=3)
                top_probs = top_probs_t.cpu().numpy()
                top_indices = top_indices_t.cpu().numpy()

            # 2. Extract results
            primary_idx = int(top_indices[0])
            confidence = float(top_probs[0])
            class_key = CLASS_NAMES[primary_idx]
            meta = DISEASE_METADATA.get(class_key, {
                'crop': class_key.split('___')[0].replace('_', ' '),
                'condition': class_key.split('___')[1].replace('_', ' '),
                'is_healthy': 'healthy' in class_key.lower(),
                'severity': 'Moderate',
                'symptoms': 'Characteristic foliar lesions observed.',
                'care': ['Monitor plant progress and isolate if symptoms spread.'],
                'prevention': 'Ensure proper sanitation and cultural hygiene.'
            })

            # Format top candidates
            candidates = []
            for prob, idx in zip(top_probs, top_indices):
                c_key = CLASS_NAMES[int(idx)]
                c_meta = DISEASE_METADATA.get(c_key, {})
                candidates.append({
                    'class_name': c_key,
                    'crop': c_meta.get('crop', c_key.split('___')[0]),
                    'condition': c_meta.get('condition', c_key.split('___')[1]),
                    'confidence': round(float(prob) * 100, 2)
                })

            # 3. Out-of-distribution & low-confidence safety check
            warning_msg = None
            entropy = float(self._entropy(np.array([float(p) for p in top_probs])))
            max_ent = float(self._max_entropy(len(CLASS_NAMES)))
            normalized_entropy = entropy / max_ent if max_ent > 0 else 0
            
            if confidence < 0.40:
                warning_msg = (
                    "Very Low Confidence: The model's top prediction is below 40%. "
                    "This image likely contains a plant, disease, or condition outside the 38 supported classes. "
                    "Do NOT rely on this result. Consult a local agricultural extension specialist."
                )
            elif confidence < 0.60:
                warning_msg = (
                    "Low Confidence: The model's top prediction is below 60%. "
                    "The image may be unclear, improperly lit, or show a condition outside the supported classes. "
                    "Treat this as a preliminary suggestion only — verify with an expert before taking action."
                )
            elif normalized_entropy > 0.7:
                warning_msg = (
                    "High Uncertainty: The model is distributing probability across many classes, "
                    "suggesting it is uncertain about this image. Verify with an expert."
                )

            # Always include the AI disclaimer
            disclaimer = (
                "This is an AI-assisted preliminary assessment, not a guaranteed diagnosis. "
                "Always verify with a qualified agricultural specialist before applying treatments. "
                "Product choice and application must follow local regulations and label instructions."
            )

            return {
                'success': True,
                'class_name': class_key,
                'crop': meta['crop'],
                'condition': meta['condition'],
                'is_healthy': meta['is_healthy'],
                'severity': meta['severity'],
                'confidence': round(confidence * 100, 2),
                'symptoms': meta['symptoms'],
                'care_recommendations': meta['care'],
                'prevention': meta['prevention'],
                'warning': warning_msg,
                'disclaimer': disclaimer,
                'top_candidates': candidates
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Image processing or inference error: {str(e)}'
            }

def get_supported_classes():
    """Returns catalog of supported crops and conditions for user reference."""
    grouped = {}
    for c_key in CLASS_NAMES:
        meta = DISEASE_METADATA.get(c_key, {})
        crop = meta.get('crop', c_key.split('___')[0])
        condition = meta.get('condition', c_key.split('___')[1])
        if crop not in grouped:
            grouped[crop] = []
        grouped[crop].append({
            'raw_class': c_key,
            'condition': condition,
            'is_healthy': meta.get('is_healthy', False)
        })
    return grouped
