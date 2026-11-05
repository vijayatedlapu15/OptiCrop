"""
OptiCrop Plant Disease Knowledge Base (disease_kb.py)
Comprehensive, plant-pathological management, prevention, treatment, recovery monitoring,
and traceable academic/extension references for all 38 benchmark PlantVillage classes across 14 host crop species.

Sources include:
- University of California Statewide Integrated Pest Management Program (UC IPM)
- Cornell Cooperative Extension / Vegetable MD Online
- Penn State Extension Tree Fruit and Vegetable Production Guides
- Indian Council of Agricultural Research (ICAR) & Krishi Vigyan Kendra (KVK) Extension Bulletins
- Food and Agriculture Organization (FAO) Plant Production and Protection Papers
"""

DISEASE_MANAGEMENT_KB = {
    'Apple___Apple_scab': {
        'crop': 'Apple',
        'condition': 'Apple Scab (Venturia inaequalis)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Venturia inaequalis (teleomorph) / Spilocaea pomi (anamorph)',
        'severity': 'Moderate to High',
        'symptoms': 'Olive-green to velvety dark brown circular lesions on upper leaf surfaces, progressing to chlorotic distortion, corky scabbed lesions on fruit, and premature defoliation.',
        'immediate_actions': [
            'Inspect adjacent canopy trees to map the spatial distribution and severity of sporulating foliar lesions.',
            'Collect and bag freshly fallen scabbed leaves beneath the canopy to minimize ascospore discharge.',
            'Avoid overhead sprinkler irrigation that prolongs leaf wetness beyond the critical infection period (6-9 hours at 15-24°C).'
        ],
        'spread_prevention': [
            'Maintain dry foliage during early morning spore-release windows.',
            'Disinfect pruning tools between trees using 70% isopropyl alcohol or 10% household bleach solution.',
            'Implement orchard floor management: flail-mow or rake fallen leaves in late autumn, or spray 5% urea solution to accelerate leaf breakdown.'
        ],
        'cultural_management': [
            'Perform annual dormant pruning to create an open canopy structure, allowing rapid wind drying and sunlight penetration.',
            'Avoid excessive nitrogen fertilization that stimulates overly lush, highly susceptible vegetative shoot growth.',
            'Space trees properly according to rootstock vigor to prevent dense microclimate humidity pockets.'
        ],
        'treatment_options': {
            'cultural': [
                'Autumn leaf removal and flail mowing to destroy pseudothecia (primary overwintering structures).',
                'Drip or micro-sprinkler irrigation directed to soil, keeping tree foliage completely dry.'
            ],
            'biological': [
                'Apply Bacillus subtilis or Bacillus amyloliquefaciens formulations during early vegetative flush as biological antagonists.',
                'Utilize certified organic copper octanoate or wettable sulfur sprays from green tip to tight cluster before rain events.'
            ],
            'chemical': [
                'Protectant fungicides: Captan (FRAC M04) or Mancozeb (FRAC M03) applied prior to predicted rain/infection events from bud break to petal fall.',
                'Curative/Systemic fungicides: DMI triazoles (e.g. Myclobutanil, FRAC 3) or SDHI fungicides (e.g. Boscalid, FRAC 7) applied within 72 hours of an infection event.',
                'Resistance management: Strictly alternate FRAC groups (e.g. rotate FRAC 3 with FRAC 7 and M04) to prevent Venturia inaequalis resistance.'
            ],
            'warnings': [
                'Pollinator Protection: DO NOT apply insecticides or fungicides during full bloom when bees are actively foraging.',
                'Phytotoxicity: Do not apply sulfur within 21 days of an oil spray or when ambient temperatures exceed 29°C (85°F).',
                'Personal Protective Equipment (PPE): Wear chemical-resistant gloves, eye goggles, and long-sleeved clothing. Adhere to statutory Re-Entry Intervals (REI) and Pre-Harvest Intervals (PHI).'
            ]
        },
        'recovery_monitoring': [
            'Inspect newly emerging leaves 7-10 days following treatment for clean, symptom-free green margins.',
            'Check established lesions for arrested fungal sporulation (lesions should turn dull brown and inactive rather than velvety olive-green).',
            'If active lesions continue expanding onto secondary spur leaves, evaluate spray coverage and fungicide resistance.'
        ],
        'prevention_next_cycle': [
            'Plant scab-resistant apple cultivars (e.g. Liberty, Enterprise, Freedom, CrimsonCrisp, GoldRush) in humid orchard zones.',
            'Perform thorough orchard ground sanitation before bud break to disrupt primary ascospore release.',
            'Install automated weather/leaf-wetness monitoring stations to time sprays with the Mills Scab Infection Period Table.'
        ],
        'expert_assistance': 'Contact a local university fruit extension specialist or KVK horticulturist if scab symptoms resist standard FRAC 3/7 chemistries or if >25% of fruit spurs show defoliation.',
        'references': [
            {'title': 'UC IPM Pest Management Guidelines: Apple Scab', 'source': 'University of California Agriculture and Natural Resources', 'url': 'https://ipm.ucanr.edu/agriculture/apple/apple-scab/'},
            {'title': 'Tree Fruit Production Guide: Apple Scab Management', 'source': 'Penn State Extension', 'url': 'https://extension.psu.edu/apple-scab'}
        ]
    },
    'Apple___Black_rot': {
        'crop': 'Apple',
        'condition': 'Black Rot & Frogeye Leaf Spot (Botryosphaeria obtusa)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Botryosphaeria obtusa (anamorph Sphaeropsis malorum)',
        'severity': 'High',
        'symptoms': 'Small purple specks on leaves enlarging into circular lesions with tan centers and purple margins (frogeye leaf spot); sunken, dark, reddish-brown cankers on branches; firm brown rotted fruit with concentric black pycnidia rings.',
        'immediate_actions': [
            'Prune out dead, damaged, or cankered twigs and limbs immediately, cutting at least 15 cm (6 inches) below visible margins into healthy wood.',
            'Remove and dispose of all mummified fruit remaining on the tree or orchard floor.',
            'Disinfect pruning tools with 70% alcohol between cuts.'
        ],
        'spread_prevention': [
            'Never leave pruned twigs or cankered wood piles in or near the orchard; burn or deep-bury infected debris.',
            'Control fire blight cankers and insect punctures (e.g. plum curculio) which serve as entry wounds for Botryosphaeria.',
            'Avoid overhead wetting of woody scaffolds.'
        ],
        'cultural_management': [
            'Maintain tree vigor through balanced soil nutrition based on leaf tissue testing; avoid excessive nitrogen that delays dormancy hardening.',
            'Protect trunks from winter sunscald and frost cracks using white tree paint or trunk guards.',
            'Prune during dry dormant periods to minimize wound infection.'
        ],
        'treatment_options': {
            'cultural': [
                'Sanitation: complete eradication of overwintered mummies and dead fire-blighted wood from the canopy.',
                'Open canopy pruning to expedite wood and foliage drying.'
            ],
            'biological': [
                'Limited commercial biological control available; preventive bio-copper formulations at green tip offer early surface suppression.'
            ],
            'chemical': [
                'Foliar protectants: Captan (FRAC M04) or Mancozeb (FRAC M03) applied from tight cluster through mid-summer.',
                'Systemic options: Thiophanate-methyl (FRAC 1) or Strobilurins (FRAC 11) tank-mixed with protectants for canker and fruit rot suppression where labeled.'
            ],
            'warnings': [
                'Fungicide sprays alone cannot control black rot if dead cankered wood and mummies remain in the tree canopy.',
                'Strictly observe Pre-Harvest Intervals (typically 14-77 days depending on active ingredient and country regulations).'
            ]
        },
        'recovery_monitoring': [
            'Monitor pruned limb stubs 14-21 days post-cut for clean callus healing without sunken bark margins.',
            'Scout developing fruitlets for firm black rot decay or pycnidial speckling.',
            'Record any secondary frogeye spotting on terminal leaf flushes.'
        ],
        'prevention_next_cycle': [
            'Perform rigorous winter sanitation: cut out all dead wood before buds swell in spring.',
            'Manage orchard nutrition to ensure trees enter winter dormancy without succulent, cold-tender tissue.'
        ],
        'expert_assistance': 'Consult an extension plant pathologist if large scaffold limbs or primary trunk crotches develop spreading necrotic cankers.',
        'references': [
            {'title': 'Black Rot of Apple', 'source': 'Cornell Cooperative Extension / NYS Integrated Pest Management', 'url': 'https://ecommons.cornell.edu/handle/1813/43076'},
            {'title': 'Frogeye Leaf Spot and Black Rot of Apple', 'source': 'Penn State Extension', 'url': 'https://extension.psu.edu/frogeye-leaf-spot-and-black-rot-of-apple'}
        ]
    },
    'Apple___Cedar_apple_rust': {
        'crop': 'Apple',
        'condition': 'Cedar Apple Rust (Gymnosporangium juniperi-virginianae)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Gymnosporangium juniperi-virginianae (Heteroecious rust fungus)',
        'severity': 'Moderate',
        'symptoms': 'Bright yellow-orange or reddish-orange circular spots on the upper leaf surface, followed by tiny black pycnia; tube-like aecia structures (cluster cups) forming on the leaf underside that shed rust spores in mid-summer.',
        'immediate_actions': [
            'Verify whether nearby eastern red cedar (Juniperus virginiana) or ornamental junipers harbor brown woody galls with orange gelatinous spore horns.',
            'Mark infected apple tree blocks for preventive spring timing; foliar lesions cannot be reversed once established on the leaf.'
        ],
        'spread_prevention': [
            'Eradicate or prune cedar galls on red cedars and junipers within a 300 to 500-meter radius of the orchard boundary if feasible.',
            'Disrupt spore drift by planting evergreen non-host windbreaks between juniper habitats and apple orchards.'
        ],
        'cultural_management': [
            'Because the fungus requires both apple (Rosaceae) and juniper (Cupressaceae) hosts to complete its life cycle, removing the alternate host eliminates infection pressure.',
            'Maintain good weed management and open tree architecture.'
        ],
        'treatment_options': {
            'cultural': [
                'Physical removal of galls from neighboring junipers during winter before gelatinous horns expand in warm rains.'
            ],
            'biological': [
                'Biological controls have very limited efficacy against cedar apple rust. Sulfur provides moderate suppression if applied before rain.'
            ],
            'chemical': [
                'Foliar protective/curative fungicides: DMI triazoles (e.g. Myclobutanil - FRAC 3) or Mancozeb (FRAC M03) applied from pink bud stage through petal fall.',
                'Strobilurin fungicides (e.g. Trifloxystrobin - FRAC 11) provide preventive control when timed with spring rainfall events.'
            ],
            'warnings': [
                'Once orange lesions and aecia have developed on apple foliage, chemical fungicide applications are ineffective for that growing season.',
                'Do not apply triazole fungicides repeatedly without rotating FRAC groups to prevent pathogen resistance.'
            ]
        },
        'recovery_monitoring': [
            'Inspect newly developing terminal shoots 10-14 days after petal-fall fungicide applications; new foliage should be completely free of orange lesions.',
            'Check fruit surfaces for early rusty chlorotic blemishes.'
        ],
        'prevention_next_cycle': [
            'Select rust-immune or highly resistant apple cultivars (e.g. Redfree, Liberty, William’s Pride, Priscilla, Enterprise) when establishing new orchard blocks.',
            'Susceptible varieties (e.g. Golden Delicious, Rome Beauty, Honeycrisp, Gala) require strict preventive fungicide scheduling from bud break through petal fall.'
        ],
        'expert_assistance': 'Contact extension agents if severe defoliation (>30% canopy) occurs on high-value commercial cultivars.',
        'references': [
            {'title': 'Cedar Apple Rust', 'source': 'Purdue University Extension', 'url': 'https://www.extension.purdue.edu/extmedia/bp/bp-137-w.pdf'},
            {'title': 'Apple Rust Diseases', 'source': 'Cornell Cooperative Extension Vegetable & Fruit MD', 'url': 'https://ecommons.cornell.edu/handle/1813/43081'}
        ]
    },
    'Apple___healthy': {
        'crop': 'Apple',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Foliage displays uniform deep green coloration, active turgor, well-formed leaf margins, and absence of necrotic, chlorotic, or fungal spotting.',
        'immediate_actions': [
            'Continue regular routine orchard scouting for early signs of mites, aphids, and foliar spotting.',
            'Record baseline tree growth and leaf canopy density.'
        ],
        'spread_prevention': [
            'Practice clean orchard sanitation to maintain disease-free status.',
            'Sterilize pruning shears between orchard blocks.'
        ],
        'cultural_management': [
            'Apply balanced irrigation using drip lines to maintain root-zone soil moisture without wetting the tree canopy.',
            'Maintain optimal soil pH (6.0 - 6.8) and supply nitrogen based on shoot growth measurements (20-40 cm shoot extension per season).'
        ],
        'treatment_options': {
            'cultural': ['Continue standard canopy thinning, balanced mulching, and weed suppression along tree strips.'],
            'biological': ['Conserve native predators such as phytoseiid predatory mites and lady beetles by avoiding broad-spectrum synthetic pyrethroids.'],
            'chemical': ['No curative chemical treatment needed. Maintain standard preventive seasonal cover sprays if in high disease-pressure humid zones.'],
            'warnings': ['Avoid unnecessary pesticide applications that harm beneficial pollinator populations and predatory mites.']
        },
        'recovery_monitoring': [
            'Conduct weekly scouting along random orchard transects.',
            'Monitor shoot growth rate, leaf color index, and fruit set.'
        ],
        'prevention_next_cycle': ['Maintain winter pruning, balanced fertilization, and post-harvest orchard floor sanitation.'],
        'expert_assistance': 'No intervention required unless uncharacteristic leaf drop or nutrient deficiency chlorosis develops.',
        'references': [
            {'title': 'Integrated Orchard Management for Apples', 'source': 'FAO Plant Production Guide', 'url': 'https://www.fao.org/publications/'}
        ]
    },
    'Blueberry___healthy': {
        'crop': 'Blueberry',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Vibrant, waxy green leaves with clean petioles, strong shoot elongation, and absence of chlorosis, necrosis, or twig dieback.',
        'immediate_actions': ['Monitor soil moisture and maintain acid root zone conditions.'],
        'spread_prevention': ['Inspect incoming nursery stock for root rot (Phytophthora) or stem blight.'],
        'cultural_management': [
            'Maintain soil pH strictly between 4.5 and 5.2 using elemental sulfur or iron sulfate.',
            'Mulch bushes with pine needles or aged softwood chips (7-10 cm depth) to preserve moisture and suppress weeds.',
            'Use drip irrigation with clean, low-salinity, low-bicarbonate water.'
        ],
        'treatment_options': {
            'cultural': ['Apply ammonium sulfate or urea fertilizer; avoid nitrate forms of nitrogen that raise soil pH.'],
            'biological': ['Encourage mycorrhizal root colonization through organic mulching and minimal root disturbance.'],
            'chemical': ['No curative treatment needed.'],
            'warnings': ['Do not over-fertilize young blueberry bushes; shallow fine roots are highly sensitive to fertilizer salt burn.']
        },
        'recovery_monitoring': ['Check foliage monthly for iron chlorosis (yellowing between leaf veins), which indicates soil pH rising above 5.5.'],
        'prevention_next_cycle': ['Annual renewal pruning of canes older than 6 years to maintain vigorous juvenile fruiting wood.'],
        'expert_assistance': 'Consult an extension berry specialist if interveinal yellowing or sudden cane collapse occurs.',
        'references': [
            {'title': 'Blueberry Pest Management Guide', 'source': 'Michigan State University Extension', 'url': 'https://www.canr.msu.edu/blueberries/'}
        ]
    },
    'Cherry_(including_sour)___Powdery_mildew': {
        'crop': 'Cherry (including sour)',
        'condition': 'Powdery Mildew (Podosphaera clandestina)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Podosphaera clandestina',
        'severity': 'Moderate',
        'symptoms': 'Patches of white, powdery fungal growth on leaves and shoots, leaf curling and upward cupping, stunted terminal growth, and deformed fruit with white mycelial scarring.',
        'immediate_actions': [
            'Prune and destroy severely infected terminal shoot tips where white powdery mycelium is dense.',
            'Halt evening overhead watering; powdery mildew thrives in high relative humidity without free standing water.'
        ],
        'spread_prevention': [
            'Improve orchard airflow to accelerate humidity dispersal around inner canopy branches.',
            'Clean pruning equipment after servicing infected blocks.'
        ],
        'cultural_management': [
            'Prune internal water sprouts and suckers during the summer to maintain light penetration and air movement.',
            'Avoid over-fertilizing with nitrogen which produces excessive, highly susceptible succulent shoots.'
        ],
        'treatment_options': {
            'cultural': ['Canopy thinning and summer pruning of dense vegetative shoots.'],
            'biological': [
                'Potassium bicarbonate (e.g. Armicarb) or horticultural mineral oil (e.g. JMS Stylet-Oil) applied at early onset to desiccate fungal mycelium.',
                'Bacillus amyloliquefaciens or Bacillus subtilis organic bio-fungicides.'
            ],
            'chemical': [
                'Protectant/Sterol Inhibitor fungicides: Myclobutanil (FRAC 3), Quinoxyfen (FRAC 13), or Fluopyram + Trifloxystrobin (FRAC 7 + 11).',
                'Wettable sulfur sprays from shuck fall through harvest on sour cherry varieties.'
            ],
            'warnings': [
                'Sulfur Phytotoxicity: Do NOT apply sulfur when temperatures exceed 29°C (85°F) or within 14 days of an oil application.',
                'Rotate fungicide mode of action (FRAC codes) to avoid Podosphaera resistance.'
            ]
        },
        'recovery_monitoring': [
            'Inspect newly emerged terminal leaves 7-10 days post-application; new tissue should remain flat and free of white powder.',
            'Examine green fruitlets for absence of reticulated russeting or powdery patches.'
        ],
        'prevention_next_cycle': [
            'Maintain rigorous post-harvest canopy pruning to reduce overwintering cleistothecia in bark crevices.',
            'Commence preventive fungicide program in spring at first leaf emergence if mildew pressure was severe in prior season.'
        ],
        'expert_assistance': 'Consult tree fruit extension specialists if fruit infection occurs or standard fungicides fail to stop shoot curl.',
        'references': [
            {'title': 'Cherry Powdery Mildew Management', 'source': 'Washington State University Tree Fruit Extension', 'url': 'http://treefruit.wsu.edu/crop-protection/disease-management/cherry-powdery-mildew/'},
            {'title': 'UC IPM: Cherry Powdery Mildew', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/cherry/powdery-mildew/'}
        ]
    },
    'Cherry_(including_sour)___healthy': {
        'crop': 'Cherry (including sour)',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Clean, lustrous green leaves, active terminal bud extension, intact leaf margins, and absence of shot-hole perforations or powdery fungal coatings.',
        'immediate_actions': ['Maintain regular orchard monitoring schedule.'],
        'spread_prevention': ['Practice clean tool sanitation and inspect for cherry leaf spot or bacterial canker.'],
        'cultural_management': [
            'Manage orchard floor cover crop to support soil organic matter and beneficial insect habitat.',
            'Provide supplemental drip irrigation during dry summer fruit-filling stages.'
        ],
        'treatment_options': {
            'cultural': ['Standard canopy maintenance and pruning of dead or broken branches.'],
            'biological': ['Conserve predatory mites and natural parasites of cherry fruit flies.'],
            'chemical': ['No curative chemical treatment needed.'],
            'warnings': ['Avoid prophylactic pesticide sprays that disrupt natural biological controls.']
        },
        'recovery_monitoring': ['Monitor weekly canopy shoot development and fruit maturation.'],
        'prevention_next_cycle': ['Perform dormant copper spray after leaf drop if bacterial canker is endemic in the area.'],
        'expert_assistance': 'Not required for healthy foliage.',
        'references': [{'title': 'Pacific Northwest Plant Disease Management Handbook: Cherry', 'source': 'Oregon State University Extension', 'url': 'https://pnwhandbooks.org/plantdisease/crop-approach/fruit-nut'}]
    },
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': {
        'crop': 'Corn (Maize)',
        'condition': 'Gray Leaf Spot (Cercospora zeae-maydis)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Cercospora zeae-maydis',
        'severity': 'High',
        'symptoms': 'Narrow, rectangular, tan-to-gray lesions strictly delimited by leaf veins running parallel to the leaf margin. Lesions coalesce under prolonged humidity, blighting large foliar sections.',
        'immediate_actions': [
            'Assess disease progression relative to the ear leaf: scout whether lesions have reached the third leaf below the ear leaf prior to tasseling (VT stage).',
            'Determine whether field conditions (prolonged dew, temperatures 24-32°C) favor continued upward epidemic spread.'
        ],
        'spread_prevention': [
            'In continuous no-till corn systems, rotate fields to non-host crops (soybean, sunflower, sorghum, or pulses) for 1-2 years to deplete residue inoculum.',
            'Where conservation guidelines permit, implement residue management (vertical tillage or shredding) to encourage corn stalk decomposition.'
        ],
        'cultural_management': [
            'Select and plant corn hybrids with strong genetic tolerance or multi-genic resistance ratings to Gray Leaf Spot.',
            'Avoid excessively high plant populations that restrict canopy ventilation and elevate relative humidity in the lower whorl.'
        ],
        'treatment_options': {
            'cultural': [
                'Crop rotation: minimum 1-year rotation away from corn.',
                'Balanced fertilization: avoid severe potassium deficits which worsen fungal leaf blight susceptibility.'
            ],
            'biological': [
                'Commercial foliar bio-fungicides currently provide insufficient control under high GLS disease pressure in field corn.'
            ],
            'chemical': [
                'Foliar fungicides: Strobilurin (QoI, FRAC 11) + Triazole (DMI, FRAC 3) or SDHI (FRAC 7) premixes (e.g. Pyraclostrobin + Fluxapyroxad, or Azoxystrobin + Difenoconazole).',
                'Application timing: Apply between VT (tasseling) and R1 (silking) if scouting shows lesions present on lower leaves and favorable weather persists.'
            ],
            'warnings': [
                'Economic Threshold: Spraying after the R3 (milk) stage rarely provides economic return.',
                'Adjuvant Safety: Do NOT apply non-ionic surfactants or crop oils between V8 and VT to prevent arrested ear syndrome.'
            ]
        },
        'recovery_monitoring': [
            'Monitor upper canopy leaves above the ear leaf 14 days post-application; the ear leaf and upper foliage should remain green and photosynthetically active through grain fill.',
            'Assess stalk integrity at maturity using the push test (pushing 20 stalks to a 45° angle) to detect early lodging risk caused by foliar blighting.'
        ],
        'prevention_next_cycle': [
            'Choose corn hybrids with high resistance scores (score 7+ on 1-9 scale).',
            'Plan 2-year crop rotation with legumes or oilseeds in continuous-corn problem fields.'
        ],
        'expert_assistance': 'Consult agricultural university crop extension specialists or local KVK agronomists if lesions reach the ear leaf prior to silking.',
        'references': [
            {'title': 'Gray Leaf Spot of Corn', 'source': 'Purdue University Extension Crop Pathology', 'url': 'https://extension.entm.purdue.edu/fieldcropsipm/diseases/gray-leaf-spot.php'},
            {'title': 'Management of Gray Leaf Spot in Corn', 'source': 'Iowa State University Extension', 'url': 'https://crops.extension.iastate.edu/cropnews/2020/07/gray-leaf-spot-corn'}
        ]
    },
    'Corn_(maize)___Common_rust_': {
        'crop': 'Corn (Maize)',
        'condition': 'Common Rust (Puccinia sorghi)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Puccinia sorghi',
        'severity': 'Moderate',
        'symptoms': 'Circular to elongate cinnamon-brown to dark golden pustules (uredinia) scattered across both upper and lower leaf surfaces. Pustules rupture the epidermis to release powdery orange-brown spores.',
        'immediate_actions': [
            'Scout fields and determine rust severity: count pustules per leaf and observe whether pustules are confined to lower leaves or moving upward.',
            'Check corn growth stage: common rust rarely causes economic damage in field corn if infection occurs after whorl stages, but sweet corn and seed production corn are vulnerable.'
        ],
        'spread_prevention': [
            'Spore spread is airborne from southern regions; field sanitation has little effect because Puccinia sorghi does not overwinter in cold northern corn residue.',
            'Scout early-planted and late-planted fields separately.'
        ],
        'cultural_management': [
            'Plant rust-resistant hybrids possessing single-gene resistance (Rp genes) or robust general/partial resistance.',
            'Ensure adequate soil potassium fertility to assist crop osmotic regulation and tissue strength.'
        ],
        'treatment_options': {
            'cultural': ['Plant resistant hybrids; time planting to avoid peak airborne urediniospore flights where seasonal migration patterns are known.'],
            'biological': ['Foliar bio-fungicides are generally unverified for broad-scale economic field corn rust control.'],
            'chemical': [
                'Fungicides: Triazoles (FRAC 3, e.g. Propiconazole, Tebuconazole) or Strobilurins (FRAC 11, e.g. Azoxystrobin, Pyraclostrobin).',
                'Timing: Applications are only economically viable in seed production or sweet corn if pustules appear prior to tasseling and weather is cool and moist (16-25°C).'
            ],
            'warnings': [
                'Commercial field/grain corn rarely warrants fungicide treatment for common rust unless hybrid resistance has broken down and severe early infection threatens the ear leaf.',
                'Adhere to Pre-Harvest Intervals and livestock grazing restrictions on treated forage.'
            ]
        },
        'recovery_monitoring': [
            'Check upper leaves 10-14 days following treatment: new leaves should emerge without dense pustule clusters.',
            'Urediniospores in treated pustules should darken to black teliospores as tissue matures.'
        ],
        'prevention_next_cycle': [
            'Select hybrids containing generalized multi-gene resistance rather than solely relying on single Rp1-D genes which rust strains may overcome.'
        ],
        'expert_assistance': 'Contact your local crop extension agent if a previously resistant hybrid shows sudden widespread rust susceptibility.',
        'references': [
            {'title': 'Common Rust of Corn', 'source': 'University of Illinois Extension Field Crop Diseases', 'url': 'http://cropdisease.cropsciences.illinois.edu/'},
            {'title': 'Corn Disease Management: Common Rust', 'source': 'University of Nebraska-Lincoln CropWatch', 'url': 'https://cropwatch.unl.edu/plantdisease/corn/common-rust'}
        ]
    },
    'Corn_(maize)___Northern_Leaf_Blight': {
        'crop': 'Corn (Maize)',
        'condition': 'Northern Corn Leaf Blight (Exserohilum turcicum)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Exserohilum turcicum (teleomorph Setosphaeria turcica)',
        'severity': 'High',
        'symptoms': 'Long, elliptical, cigar-shaped grayish-green to tan lesions (2.5 to 15 cm long and 1-2 cm wide) with smooth edges. In humid weather, dark olive-gray fungal sporulation develops on lesion centers.',
        'immediate_actions': [
            'Examine the lower third of the canopy: count the number of cigar-shaped lesions on leaves below the ear leaf.',
            'Determine whether warm (18-27°C) and persistent rainy/dewy conditions are forecast during early reproductive development.'
        ],
        'spread_prevention': [
            'Rotate away from corn for at least 1-2 years in continuous no-till fields to reduce overwintered chlamydospores and conidia in corn residue.',
            'Perform conservation tillage or stalk chopping to accelerate residue microbial decomposition.'
        ],
        'cultural_management': [
            'Select corn hybrids with strong Ht-gene resistance (Ht1, Ht2, Ht3, or HtN) combined with polygenic background tolerance.',
            'Optimize planting density to promote airflow across the lower canopy.'
        ],
        'treatment_options': {
            'cultural': [
                'Crop rotation with non-host crops (soybean, small grains, pulses).',
                'Residue management and balanced balanced fertility.'
            ],
            'biological': [
                'No commercially verified biological foliar spray for broadacre grain production.'
            ],
            'chemical': [
                'Foliar fungicides: Mixed-mode fungicides containing Strobilurins (FRAC 11) + Triazoles (FRAC 3) or SDHI (FRAC 7) (e.g. Azoxystrobin + Propiconazole, or Pyraclostrobin + Fluxapyroxad).',
                'Application window: Apply between VT and R2 if lesions are detected on or near the ear leaf before blister stage.'
            ],
            'warnings': [
                'Applications made after the R3 (milk) stage provide negligible economic return.',
                'Rotate active ingredient classes to preserve fungicide efficacy against Exserohilum.'
            ]
        },
        'recovery_monitoring': [
            'Check the upper three leaves and the ear leaf 14 days post-application; lesions should not advance into the upper canopy.',
            'Evaluate stalk strength near harvest to identify fields with high premature lodging risk.'
        ],
        'prevention_next_cycle': [
            'Select hybrids with high disease ratings for Northern Corn Leaf Blight.',
            'Avoid planting highly susceptible hybrids in river valleys or sheltered low-lying fields prone to extended morning dew.'
        ],
        'expert_assistance': 'Consult your regional agricultural extension specialist if lesions develop on the ear leaf before tassel emergence.',
        'references': [
            {'title': 'Northern Corn Leaf Blight', 'source': 'Purdue University Extension', 'url': 'https://extension.entm.purdue.edu/fieldcropsipm/diseases/northern-corn-leaf-blight.php'},
            {'title': 'Managing Northern Corn Leaf Blight', 'source': 'University of Minnesota Extension', 'url': 'https://extension.umn.edu/corn-pest-management/northern-corn-leaf-blight'}
        ]
    },
    'Corn_(maize)___healthy': {
        'crop': 'Corn (Maize)',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Broad, deep green leaves with smooth intact margins, clean veins, vigorous whorl or tassel development, and absence of necrotic blights or chlorotic striping.',
        'immediate_actions': ['Continue standard field scouting at V6, VT, and R1 reproductive stages.'],
        'spread_prevention': ['Maintain clean farm machinery when moving between different production blocks.'],
        'cultural_management': [
            'Maintain optimal soil fertility: ensure side-dressed nitrogen is timed with peak uptake (V8-V12 stage).',
            'Schedule irrigation to prevent drought stress during the critical silking and pollination window (R1).'
        ],
        'treatment_options': {
            'cultural': ['Standard agronomic weed control and soil fertility management.'],
            'biological': ['Conserve beneficial insect predators (lady beetles, lacewings) that feed on corn leaf aphids and corn borer eggs.'],
            'chemical': ['No curative chemical treatment needed.'],
            'warnings': ['Do not apply unnecessary maintenance fungicides without scouting verification of disease pressure.']
        },
        'recovery_monitoring': ['Monitor tassel emergence, silk elongation, and kernel blister development.'],
        'prevention_next_cycle': ['Rotate with legumes to naturally replenish soil nitrogen and suppress specialized corn pathogens.'],
        'expert_assistance': 'No action required for healthy corn.',
        'references': [{'title': 'Corn Field Scouting Guide', 'source': 'Iowa State University Extension', 'url': 'https://store.extension.iastate.edu/'}]
    },
    'Grape___Black_rot': {
        'crop': 'Grape',
        'condition': 'Grape Black Rot (Guignardia bidwellii)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Guignardia bidwellii (anamorph Phyllosticta ampelicida)',
        'severity': 'High',
        'symptoms': 'Circular reddish-brown leaf spots with dark margins and tiny black pycnidia pimples arranged in a ring; berries develop light brown soft spots, quickly turning into hard, shriveled, black wrinkled mummies that cling to the cluster.',
        'immediate_actions': [
            'Hand-prune and remove infected cluster mummies and blighted shoot tips; bag and destroy them away from the vineyard.',
            'Ensure canopy canopy shoot positioning allows rapid drying after rain.'
        ],
        'spread_prevention': [
            'Overwintered mummified berries on the vineyard floor or hanging in trellises are the primary source of spring ascospores; remove all mummies during winter pruning.',
            'Avoid working in wet vineyard rows to prevent splash dispersal of pycnidiospores.'
        ],
        'cultural_management': [
            'Perform canopy management (shoot thinning, leaf pulling around fruiting zones, shoot positioning) to maximize sun exposure and wind airflow.',
            'Keep vineyard floor mowed clean to prevent high humidity microclimates beneath the trellis.'
        ],
        'treatment_options': {
            'cultural': [
                'Strict winter sanitation: drop and bury or shred all mummies before bud break.',
                'Open canopy trellis systems (VSP, Scott Henry) that dry within 2 hours of rainfall.'
            ],
            'biological': [
                'Bio-fungicides offer limited protection under high black rot pressure; copper and sulfur provide only moderate early-season suppression.'
            ],
            'chemical': [
                'Protectants: Mancozeb (FRAC M03) or Captan (FRAC M04) applied from early shoot growth (2-3 inches) through bloom.',
                'Systemic options: DMI triazoles (e.g. Myclobutanil, Tebuconazole - FRAC 3) or Strobilurins (e.g. Azoxystrobin, Kresoxim-methyl - FRAC 11) applied from immediate pre-bloom to 4 weeks post-bloom (the critical fruit protection window).'
            ],
            'warnings': [
                'Berries remain highly susceptible from bloom until 4-5 weeks post-bloom; sprays applied after berries reach veraison cannot cure established infections.',
                'Mancozeb has a 66-day Pre-Harvest Interval (PHI) on grapes in many jurisdictions; verify local label restrictions.'
            ]
        },
        'recovery_monitoring': [
            'Inspect developing grape clusters 10-14 days after post-bloom fungicide applications for clean, expanding green berries without sunken brown rot rings.',
            'Scout upper terminal leaves for secondary frogeye-like leaf lesions.'
        ],
        'prevention_next_cycle': [
            'Meticulous dormant pruning: inspect every vine and cut away every single dried mummy clinging to the trellis wires.',
            'Cultivar selection: European Vitis vinifera cultivars and French-American hybrids vary in susceptibility; plan tighter spray schedules for highly susceptible varieties (e.g. Concord, Niagara, Chardonnay).'
        ],
        'expert_assistance': 'Consult viticulture extension specialists if berry rot spreads rapidly across clusters despite pre-bloom fungicide applications.',
        'references': [
            {'title': 'Grape Black Rot Management', 'source': 'Cornell Cooperative Extension Fruit Resources', 'url': 'https://grapesandwine.cals.cornell.edu/newsletters/appellation-cornell/2011-web-articles/issue-5/black-rot/'},
            {'title': 'UC IPM Pest Management Guidelines: Grape Black Rot', 'source': 'University of California IPM', 'url': 'https://ipm.ucanr.edu/agriculture/grape/black-rot/'}
        ]
    },
    'Grape___Esca_(Black_Measles)': {
        'crop': 'Grape',
        'condition': 'Esca / Black Measles (Grapevine Trunk Disease Complex)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Complex of Phaeomoniella chlamydospora, Phaeoacremonium minimum, and Fomitiporia mediterranea / basidiomycetes',
        'severity': 'High (Chronic / Destructive)',
        'symptoms': 'Tiger-stripe interveinal chlorosis and necrosis on mature leaves (yellow and brown striping between dark green veins); small dark purple or brown spots on fruit (measles); sudden apoplexy (rapid vine collapse and wilting in hot summer); dark vascular streaking inside cordons/trunks.',
        'immediate_actions': [
            'Mark and tag symptomatic vines during mid-summer; note whether symptoms are chronic (tiger-stripe) or acute apoplexy (sudden collapse).',
            'Do NOT prune symptomatic vines during wet periods when fungal spores enter pruning wounds.'
        ],
        'spread_prevention': [
            'Protect large pruning wounds using wound sealants, acrylic paint, or registered biocontrols (e.g. Trichoderma formulations) immediately after cutting.',
            'Adopt delayed pruning (pruning in late winter just before bud break when wound healing is most rapid).',
            'Disinfect pruning saws between vines when cutting through older cordons.'
        ],
        'cultural_management': [
            'Trunk renewal: train a healthy basal sucker/water sprout to replace the diseased trunk, then amputate the diseased wood below vascular staining.',
            'Double pruning: pre-prune canes to 30-40 cm in winter, then make the final spur cut late in the dormant season.',
            'Maintain vine balance and avoid severe water stress or over-cropping that triggers sudden apoplectic collapse.'
        ],
        'treatment_options': {
            'cultural': [
                'Surgical trunk renewal and pruning wound protection.',
                'Sanitation: remove and burn dead grapevine wood, dead arms, and old cordons from the vineyard.'
            ],
            'biological': [
                'Trichoderma atroviride / Trichoderma harzianum wound dressings applied immediately to fresh pruning cuts.'
            ],
            'chemical': [
                'Foliar synthetic fungicides DO NOT CURE ESCA once established inside the woody vascular system.',
                'Pruning wound protectants: thiophanate-methyl paste or copper-based paints applied directly to large cuts immediately after pruning.'
            ],
            'warnings': [
                'CRITICAL NOTICE: Spraying foliar fungicides will NOT cure Esca. The pathogens reside deep inside woody perennial trunk tissues.',
                'Do not make large cuts during rainy weather when airborne ascospores are abundant.'
            ]
        },
        'recovery_monitoring': [
            'Monitor renewed suckers for vigorous upright growth without tiger-stripe foliar symptoms over subsequent 2 seasons.',
            'Inspect fruit clusters on surviving cordons at veraison for black measles speckling.'
        ],
        'prevention_next_cycle': [
            'Buy certified disease-tested planting material from reputable grapevine nurseries.',
            'Protect all pruning wounds every single season starting from year two of vineyard establishment.'
        ],
        'expert_assistance': 'Consult a viticultural pathologist for diagnostic wood cross-sectioning and trunk renewal surgery guidance.',
        'references': [
            {'title': 'Grapevine Trunk Diseases: Esca', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/grape/esca-black-measles/'},
            {'title': 'Managing Grapevine Trunk Diseases', 'source': 'Australian Grape and Wine Authority / AWRI', 'url': 'https://www.awri.com.au/'}
        ]
    },
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': {
        'crop': 'Grape',
        'condition': 'Isariopsis Leaf Blight (Pseudocercospora cladosporioides)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Pseudocercospora cladosporioides (syn. Isariopsis cladosporioides / Phaeoisariopsis vitis)',
        'severity': 'Moderate',
        'symptoms': 'Irregular brown to dark reddish-brown necrotic spots with distinct yellow halos on mature leaves; dark olive fungal sporulation appears on the undersides of lesions in humid conditions; premature leaf defoliation in late summer.',
        'immediate_actions': [
            'Inspect canopy interior for premature lower leaf drop and assess cluster shading.',
            'Ensure canopy airflow allows rapid morning drying.'
        ],
        'spread_prevention': [
            'Collect and shred fallen autumn leaves to eliminate overwintering mycelium and chlamydospores.',
            'Avoid excessive vegetative canopy crowding through shoot positioning.'
        ],
        'cultural_management': [
            'Perform shoot thinning, leaf pulling in the fruiting zone, and summer hedging to maintain sunlight exposure.',
            'Avoid overhead sprinkler irrigation.'
        ],
        'treatment_options': {
            'cultural': ['Canopy shoot positioning and autumn sanitation.'],
            'biological': ['Copper hydroxide or copper sulfate formulations applied preventively provide good protection.'],
            'chemical': [
                'Protectant fungicides: Mancozeb (FRAC M03), Chlorothalonil (where registered for grape), or Copper hydroxide (FRAC M01).',
                'Systemic options: Strobilurins (FRAC 11) or Triazoles (FRAC 3) applied at first lesion appearance in mid-summer.'
            ],
            'warnings': [
                'Observe Pre-Harvest Intervals (PHI) carefully; do not apply copper or mancozeb within 30-66 days of harvest depending on local enology regulations to avoid wine fermentation delays.'
            ]
        },
        'recovery_monitoring': [
            'Inspect mid-canopy leaves 10-14 days following treatment; existing spots should dry out without expanding or generating velvety sporulation.',
            'Ensure premature leaf drop ceases so vines retain sufficient leaf area for berry sugar accumulation.'
        ],
        'prevention_next_cycle': [
            'Incorporate post-harvest orchard floor sanitation to reduce fungal overwintering.',
            'Plan early summer preventive cover sprays if historical leaf blight occurs annually in the block.'
        ],
        'expert_assistance': 'Contact a viticulture extension agent if premature defoliation affects more than 20% of the leaf canopy before veraison.',
        'references': [
            {'title': 'Foliar Diseases of Grape: Pseudocercospora', 'source': 'ICAR-National Research Centre for Grapes (India)', 'url': 'https://nrcgrapes.icar.gov.in/'},
            {'title': 'Compendium of Grape Diseases', 'source': 'American Phytopathological Society (APS)', 'url': 'https://www.apsnet.org/'}
        ]
    },
    'Grape___healthy': {
        'crop': 'Grape',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Vibrant green palmate leaves, strong shoot extension, clean petiole sinuses, uniform bunch development, and complete absence of necrosis, chlorosis, or measles spotting.',
        'immediate_actions': ['Maintain routine vineyard scouting for powdery mildew, downy mildew, and leafhoppers.'],
        'spread_prevention': ['Sanitize pruning shears between blocks and manage vineyard floor cover.'],
        'cultural_management': [
            'Maintain shoot positioning in the trellis wire system.',
            'Regulate deficit irrigation (RDI) between fruit set and veraison to control canopy vigor and concentrate fruit flavors.'
        ],
        'treatment_options': {
            'cultural': ['Standard shoot thinning, suckering, and leaf removal around clusters.'],
            'biological': ['Conserve beneficial predatory mites (Typhlodromus pyri) and parasitoid wasps.'],
            'chemical': ['No curative chemical treatment needed.'],
            'warnings': ['Avoid routine broad-spectrum sprays that induce secondary spider mite flare-ups.']
        },
        'recovery_monitoring': ['Monitor shoot tip elongation; shoot tips should slow growth naturally as veraison approaches.'],
        'prevention_next_cycle': ['Perform precise dormant pruning and apply wound sealants to prevent trunk pathogen ingress.'],
        'expert_assistance': 'Not required for healthy grapevines.',
        'references': [{'title': 'Grape Pest Management', 'source': 'University of California Division of Agriculture and Natural Resources', 'url': 'https://anrcatalog.ucanr.edu/'}]
    },
    'Orange___Haunglongbing_(Citrus_greening)': {
        'crop': 'Orange',
        'condition': 'Citrus Greening / Huanglongbing (Candidatus Liberibacter asiaticus)',
        'is_healthy': False,
        'pathogen_type': 'Bacterial (Phloem-limited, insect-vectored)',
        'causal_agent': 'Candidatus Liberibacter asiaticus (vectored by Asian Citrus Psyllid, Diaphorina citri)',
        'severity': 'Critical / Quarantine Hazard',
        'symptoms': 'Asymmetric blotchy yellow mottle on mature leaves (crossing leaf veins unevenly, unlike symmetric zinc deficiency); thickened, vein-corking; twig dieback; lopsided, bitter, poorly colored fruit with inverted color break (ripening from stem down) and aborted seeds.',
        'immediate_actions': [
            'CRITICAL QUARANTINE PROTOCOL: Immediately notify your local agricultural commissioner, USDA-APHIS, or state/provincial department of agriculture.',
            'Do NOT move plant material, scion wood, or nursery stock off the property.',
            'Inspect trees for the vector: Asian Citrus Psyllid (Diaphorina citri) — tiny 3-4 mm insects feeding at a 45° angle on tender young flushes with white waxy honeydew secretions.'
        ],
        'spread_prevention': [
            'Vector suppression: manage Asian citrus psyllid populations using registered systemic insecticides (e.g. Imidacloprid, Thiamethoxam) or contact sprays during synchronized flush periods.',
            'Rogueing: in low-prevalence areas, infected trees MUST be removed immediately (cut down and stump-treated with herbicide) to prevent the tree from acting as an inoculum reservoir.',
            'Use only certified disease-free nursery trees grown under protective insect-screened structures.'
        ],
        'cultural_management': [
            'Maintain enhanced nutritional foliar programs (micro-nutrients: Zn, Mn, Fe, B) and controlled release fertilizers to sustain production in endemic regions, though nutrition does NOT cure the bacteria.',
            'Install yellow sticky traps to continuously monitor psyllid flight activity.'
        ],
        'treatment_options': {
            'cultural': [
                'Tree eradication (rogueing) of symptomatic trees in non-endemic or eradication zones.',
                'Screened greenhouse production of certified clean budwood.'
            ],
            'biological': [
                'Release of beneficial parasitoid wasps (Tamarixia radiata) for biological suppression of Asian citrus psyllid nymphs.',
                'Application of horticultural mineral oils or kaolin clay to repel psyllid feeding on young flushes.'
            ],
            'chemical': [
                'FUNGICIDES DO NOT WORK: Huanglongbing is caused by a phloem-limited bacterium; applying fungicides is completely useless.',
                'Vector control: Systemic neonicotinoids or pyrethroids targeted at ACP psyllid flushes according to local area-wide management programs.',
                'Antibiotic injection (e.g. Oxytetracycline) is strictly regulated under emergency labels in select commercial regions; consult local extension.'
            ],
            'warnings': [
                'STRICT WARNING: There is no known chemical cure for Citrus Greening once a tree is systemically infected.',
                'Observe all regional quarantine boundaries and pesticide bee-safety rules on flowering citrus.'
            ]
        },
        'recovery_monitoring': [
            'Symptomatic trees will decline over 3-5 years without intensive therapy; monitor adjacent trees monthly for blotchy mottle.',
            'Submit petiole samples to an accredited plant diagnostic lab for quantitative PCR (qPCR) molecular confirmation.'
        ],
        'prevention_next_cycle': [
            'Plant only certified pathogen-tested citrus varieties inside registered insect-proof exclusion structures.',
            'Participate in regional Area-Wide Psyllid Management Programs.'
        ],
        'expert_assistance': 'MANDATORY: Contact local university citrus extension specialists or national quarantine authorities immediately upon suspected detection.',
        'references': [
            {'title': 'Huanglongbing (Citrus Greening)', 'source': 'UC IPM Pest Management Guidelines: Citrus', 'url': 'https://ipm.ucanr.edu/agriculture/citrus/citrus-greening-huanglongbing/'},
            {'title': 'Citrus Greening Disease Information', 'source': 'USDA Animal and Plant Health Inspection Service (APHIS)', 'url': 'https://www.aphis.usda.gov/aphis/resources/pests-diseases/hungry-pests/the-threat/citrus-greening/citrus-greening-hp'}
        ]
    },
    'Peach___Bacterial_spot': {
        'crop': 'Peach',
        'condition': 'Bacterial Spot (Xanthomonas arboricola pv. pruni)',
        'is_healthy': False,
        'pathogen_type': 'Bacterial',
        'causal_agent': 'Xanthomonas arboricola pv. pruni',
        'severity': 'High',
        'symptoms': 'Small, angular, water-soaked purple-brown to black spots on leaves, often concentrated along the midrib and leaf tip; centers dry out and drop out, creating a "shot-hole" appearance; pitted, cracked, gum-exuding lesions on fruit.',
        'immediate_actions': [
            'Inspect orchard topography: check whether symptoms are most severe in sandy, wind-exposed sections.',
            'Halt any overhead irrigation that splashes bacteria between branches.'
        ],
        'spread_prevention': [
            'Establish evergreen windbreaks around sandy orchard borders to reduce windblown sand abrasions that create bacterial entry wounds.',
            'Disinfect pruning tools regularly; prune trees during dry summer weather rather than wet spring periods.'
        ],
        'cultural_management': [
            'Avoid excessive nitrogen fertilization that stimulates tender, highly susceptible vegetative growth.',
            'Maintain balanced potassium and zinc levels to promote firm cuticular leaf barriers.'
        ],
        'treatment_options': {
            'cultural': [
                'Erect windbreaks and maintain orchard floor ground cover to prevent wind-borne sand abrasion.'
            ],
            'biological': [
                'Bacteriophage treatments (where registered) or Bacillus-based biological bactericides applied preventively.'
            ],
            'chemical': [
                'FUNGICIDES ARE INEFFECTIVE: This is a bacterial pathogen.',
                'Dormant bactericides: Fixed copper (e.g. Copper hydroxide, Basic copper sulfate - FRAC M01) applied from late dormancy to early bud swell.',
                'In-season protectants: Low-rate fixed copper formulations or Oxytetracycline (FRAC 41) applied from shuck split at 7-14 day intervals until 3 weeks before harvest.'
            ],
            'warnings': [
                'Copper Phytotoxicity Hazard: Peach foliage is extremely sensitive to copper injury. Never apply high-rate copper after petal fall or during cool, slow-drying conditions, as severe defoliation will occur.',
                'Observe Pre-Harvest Intervals strictly for oxytetracycline.'
            ]
        },
        'recovery_monitoring': [
            'Monitor newly developing leaf flushes 10-14 days post-application; new leaves should show intact margins without angular purplish shot-holes.',
            'Inspect fruitlets for absence of gum-oozing pitted cracks.'
        ],
        'prevention_next_cycle': [
            'Plant peach cultivars with verified resistance to bacterial spot (e.g. Clayton, Harrow Diamond, Candor, Biscoe, PF-1, Reliance).',
            'Avoid highly susceptible varieties (e.g. O’Henry, Autumnstar, Sunprince) in sandy, windy sites.'
        ],
        'expert_assistance': 'Consult a stone fruit extension specialist if severe defoliation (>25%) occurs before pit hardening.',
        'references': [
            {'title': 'Bacterial Spot of Peach', 'source': 'Penn State Extension Tree Fruit Pathology', 'url': 'https://extension.psu.edu/bacterial-spot-of-peach'},
            {'title': 'Management of Bacterial Spot of Peach', 'source': 'University of Georgia Extension', 'url': 'https://extension.uga.edu/'}
        ]
    },
    'Peach___healthy': {
        'crop': 'Peach',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Vibrant lanceolate green leaves with finely serrated margins, clean leaf undersides, absence of shot-hole punctures or leaf curl distortion.',
        'immediate_actions': ['Maintain standard seasonal orchard scouting.'],
        'spread_prevention': ['Inspect orchard for early peach leaf curl or oriental fruit moth damage.'],
        'cultural_management': [
            'Ensure adequate irrigation during pit hardening and final fruit swell.',
            'Perform center-canopy summer pruning to allow sunlight onto interior fruiting wood.'
        ],
        'treatment_options': {
            'cultural': ['Thin developing fruitlets to 15-20 cm apart to ensure large fruit size and prevent limb breakage.'],
            'biological': ['Conserve generalist predators that feed on green peach aphids.'],
            'chemical': ['No curative chemical treatment needed.'],
            'warnings': ['Avoid broad-spectrum pesticide sprays during full bloom to safeguard pollinators.']
        },
        'recovery_monitoring': ['Track shoot elongation and fruit diameter expansion weekly.'],
        'prevention_next_cycle': ['Plan a single dormant copper/chlorothalonil spray before bud swell in winter to prevent Peach Leaf Curl (Taphrina deformans).'],
        'expert_assistance': 'Not required for healthy trees.',
        'references': [{'title': 'Peach Production Guide', 'source': 'Rutgers New Jersey Agricultural Experiment Station', 'url': 'https://njaes.rutgers.edu/'}]
    },
    'Pepper,_bell___Bacterial_spot': {
        'crop': 'Pepper (Bell)',
        'condition': 'Bacterial Spot (Xanthomonas campestris pv. vesicatoria)',
        'is_healthy': False,
        'pathogen_type': 'Bacterial',
        'causal_agent': 'Xanthomonas euvesicatoria / X. vesicatoria / X. perforans / X. gardneri',
        'severity': 'High',
        'symptoms': 'Small, water-soaked, circular-to-irregular dark spots on leaves, becoming necrotic and surrounded by a narrow yellow halo; leaf drop occurs rapidly under high disease pressure; fruit develops raised, brown, warty blisters.',
        'immediate_actions': [
            'Do NOT work in pepper fields while foliage is wet from dew or rain; bacterial cells spread rapidly via equipment and clothing.',
            'Sanitize hands, footwear, and harvest bins with disinfectant before moving to uninfected rows.'
        ],
        'spread_prevention': [
            'Switch from overhead sprinkler irrigation to drip irrigation beneath plastic mulch.',
            'Remove and destroy severely blighted plants at early localized hot-spots.'
        ],
        'cultural_management': [
            'Practice at least a 2-year crop rotation with non-solanaceous crops (e.g. sweet corn, beans, cucurbits).',
            'Use hot-water treated or certified disease-free seed tested for Xanthomonas.',
            'Plow under crop residues immediately after final harvest to accelerate bacterial decomposition.'
        ],
        'treatment_options': {
            'cultural': [
                'Drip irrigation under black plastic mulch to eliminate soil splash.',
                'Crop rotation away from tomato, eggplant, and pepper for 2-3 seasons.'
            ],
            'biological': [
                'Bacteriophage foliar sprays (e.g. AgriPhage) applied during cool evening hours.',
                'Bacillus amyloliquefaciens strain D747 or Bacillus subtilis preventive applications.'
            ],
            'chemical': [
                'FUNGICIDES ALONE DO NOT WORK: This is a bacterial pathogen.',
                'Bactericides: Fixed copper (FRAC M01, e.g. Copper hydroxide) tank-mixed with Mancozeb (FRAC M03). The copper-mancozeb tank mix releases free copper ions that enhance bacterial kill even against copper-tolerant Xanthomonas strains.',
                'Plant activators: Acibenzolar-S-methyl (Actigard, FRAC P01) applied preventively to stimulate systemic acquired resistance (SAR).'
            ],
            'warnings': [
                'Copper-resistant strains of Xanthomonas are widespread globally; pure copper sprays without mancozeb or SAR activators often fail.',
                'Observe Pre-Harvest Intervals (PHI) and worker Re-Entry Intervals (REI).'
            ]
        },
        'recovery_monitoring': [
            'Inspect newly emerging upper canopy leaves 7-10 days following treatment: new growth should be completely clean and free of water-soaked spots.',
            'Monitor lower canopy defoliation rate; rapid leaf drop indicates need for tighter bactericide intervals.'
        ],
        'prevention_next_cycle': [
            'Plant bell pepper hybrids possessing multi-race bacterial spot resistance (races 1-10 resistance, e.g. Aristotle, Playmaker, Ninja, Turnpike).',
            'Ensure seedling transplant greenhouses maintain strict sanitation and zero overhead splash.'
        ],
        'expert_assistance': 'Contact your local vegetable extension educator or KVK pathologist if resistant pepper varieties develop severe spotting.',
        'references': [
            {'title': 'Bacterial Spot of Pepper and Tomato', 'source': 'Cornell Cooperative Extension Vegetable MD Online', 'url': 'http://vegetablemdonline.ppath.cornell.edu/factsheets/Tomato_BacterialSpot.htm'},
            {'title': 'UC IPM: Pepper Bacterial Spot', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/pepper/bacterial-spot/'}
        ]
    },
    'Pepper,_bell___healthy': {
        'crop': 'Pepper (Bell)',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Dark green, smooth, lustrous leaves with uniform turgor, symmetrical growth, and complete absence of water-soaked lesions, mosaics, or necrotic spotting.',
        'immediate_actions': ['Maintain standard vegetable scouting schedule.'],
        'spread_prevention': ['Control aphid and thrips vectors to prevent virus introduction.'],
        'cultural_management': [
            'Maintain regular drip irrigation and fertigation to prevent blossom-end rot (calcium deficiency linked to moisture fluctuations).',
            'Maintain soil pH at 6.2 - 6.8.'
        ],
        'treatment_options': {
            'cultural': ['Stake or trellis pepper plants to support heavy fruit load and prevent branch breakage.'],
            'biological': ['Conserve minute pirate bugs (Orius) and predatory mites that suppress thrips.'],
            'chemical': ['No curative treatment needed.'],
            'warnings': ['Avoid excessive nitrogen that produces giant leafy vegetative bushes with poor fruit set.']
        },
        'recovery_monitoring': ['Monitor weekly flowering nodes, fruit set, and uniform canopy development.'],
        'prevention_next_cycle': ['Rotate with brassicas or legumes to maintain balanced soil health.'],
        'expert_assistance': 'Not required for healthy bell peppers.',
        'references': [{'title': 'Bell Pepper Production Guide', 'source': 'University of Florida IFAS Extension', 'url': 'https://edis.ifas.ufl.edu/'}]
    },
    'Potato___Early_blight': {
        'crop': 'Potato',
        'condition': 'Early Blight (Alternaria solani)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Alternaria solani',
        'severity': 'Moderate to High',
        'symptoms': 'Dark brown to black circular lesions displaying distinctive concentric rings ("target-board" pattern); spots initially appear on older lower foliage, surrounded by a narrow chlorotic halo; severe infection causes leaf yellowing, desiccation, and premature vine death.',
        'immediate_actions': [
            'Scout the lower third of the potato canopy to determine whether target-board lesions are spreading onto mid-canopy leaves.',
            'Check plant stress factors: early blight accelerates when potatoes enter heavy tuber bulking or suffer from nitrogen deficit.'
        ],
        'spread_prevention': [
            'Avoid overhead sprinkler irrigation late in the afternoon or evening; ensure foliage dries before sunset.',
            'Disinfect potato harvesters and equipment between fields.'
        ],
        'cultural_management': [
            'Maintain plant vigor through balanced nitrogen fertility based on petiole nitrate testing; nitrogen deficiency triggers early senescence and severe Alternaria attack.',
            'Implement a 3-year crop rotation with non-solanaceous crops (grains, corn, forage legumes).',
            'Destroy volunteer potatoes and solanaceous weeds (nightshade).'
        ],
        'treatment_options': {
            'cultural': [
                'Maintain steady irrigation to avoid alternating dry-wet soil cycles.',
                'Ensure vine desiccation/killing is complete prior to harvest to prevent tuber skinning.'
            ],
            'biological': [
                'Bio-fungicides (Bacillus subtilis, copper compounds) provide partial preventive suppression on low-pressure organic crops.'
            ],
            'chemical': [
                'Protectant fungicides: Chlorothalonil (FRAC M05) or Mancozeb (FRAC M03) applied prior to row closure at 7-10 day intervals.',
                'Targeted systemic fungicides: SDHI fungicides (e.g. Boscalid, Fluxapyroxad - FRAC 7), DMI triazoles (e.g. Difenoconazole - FRAC 3), or Pyrimethanil (FRAC 9).',
                'Resistance Note: Alternaria solani has developed widespread resistance to QoI/Strobilurin (FRAC 11) fungicides; do NOT rely on solo strobilurins.'
            ],
            'warnings': [
                'Strictly rotate FRAC codes (e.g. alternate FRAC 7 with FRAC 3 and FRAC M05) to manage fungicide resistance.',
                'Observe statutory Pre-Harvest Intervals (typically 7-14 days for potato protectants).'
            ]
        },
        'recovery_monitoring': [
            'Inspect middle and upper canopy leaves 7-10 days post-spray: new leaf tissue should remain bright green without target-like concentric rings.',
            'Observe lesion centers: treated spots should desiccate into brittle, non-sporulating brown tissue.'
        ],
        'prevention_next_cycle': [
            'Plant certified disease-free seed tubers with high physiological age vigor.',
            'Select potato varieties with moderate to high foliar resistance to early blight.',
            'Incorporate or deep-plow potato vine residue after harvest.'
        ],
        'expert_assistance': 'Consult potato extension agronomists or local KVK scientists if early blight defoliates the middle canopy before tuber bulking is complete.',
        'references': [
            {'title': 'Potato Early Blight', 'source': 'University of Idaho Extension Potato Pathology', 'url': 'https://www.uidaho.edu/extension/potatoes/'},
            {'title': 'UC IPM: Potato Early Blight', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/potato/early-blight/'}
        ]
    },
    'Potato___Late_blight': {
        'crop': 'Potato',
        'condition': 'Late Blight (Phytophthora infestans)',
        'is_healthy': False,
        'pathogen_type': 'Oomycete (Water Mold)',
        'causal_agent': 'Phytophthora infestans (Heterothallic Oomycete)',
        'severity': 'Critical / Epidemic Hazard',
        'symptoms': 'Large, irregular, water-soaked, dark greenish-brown to black lesions rapidly expanding on leaves and stems; white delicate fungal-like mildew sporulation visible on the underside of lesions under humid/cool conditions; foliage collapses with a foul decaying odor; tubers develop a firm, dry, reddish-brown granular rot beneath the skin.',
        'immediate_actions': [
            'HIGH EPIDEMIC ALERT: Phytophthora infestans can destroy entire fields within 7-10 days under favorable cool (12-20°C), wet conditions.',
            'Immediately scout the entire field to map the disease epicenter.',
            'Rogue and destroy infected plants in small localized patches: kill with contact herbicide, bag, or deeply bury (minimum 1 meter depth).'
        ],
        'spread_prevention': [
            'Destroy all cull potato piles and volunteer potatoes immediately; cull piles are the primary source of initial spring sporangia.',
            'Immediately notify neighboring potato and tomato growers to enable preventative community protection.'
        ],
        'cultural_management': [
            'Hill soil deeply around rows to create a minimum 10-15 cm soil barrier over developing tubers, preventing swimming zoospores from washing down into tubers.',
            'Terminate irrigation immediately if late blight is active in the field.',
            'Kill vines completely (chemically or mechanically) at least 14 days before harvest so that all foliar sporangia die before tubers are lifted.'
        ],
        'treatment_options': {
            'cultural': [
                'Complete eradication of cull piles and volunteer potatoes.',
                'Vine desiccation 2 weeks prior to harvest to prevent tuber inoculation during digging.'
            ],
            'biological': [
                'Fixed copper formulations (FRAC M01) provide organic protectant surface barriers, but CANNOT rescue plants once internal infection occurs.'
            ],
            'chemical': [
                'CRITICAL PATHOGEN NOTE: Phytophthora infestans is an OOMYCETE, not a true fungus. Many standard fungicides have ZERO efficacy against oomycetes.',
                'Preventive protectants: Chlorothalonil (FRAC M05), Mancozeb (FRAC M03), or Fluazinam (FRAC 29).',
                'Specialized Oomycete-targeted systemics: Mandipropamid (FRAC 40, Revus), Fluopicolide (FRAC 43), Cyazofamid (FRAC 21, Ranman), Cymoxanil (FRAC 27, Curzate - translaminar kickback activity), or Propamocarb (FRAC 28).',
                'Mefenoxam/Metalaxyl (FRAC 4) warning: Many contemporary P. infestans clonal lineages (e.g. US-23, EU-13) are MEFENOXAM-RESISTANT. Do not apply mefenoxam without laboratory confirmation of clonal sensitivity.'
            ],
            'warnings': [
                'Spray intervals must be tightened to 5 days under continuous cool, foggy, or rainy conditions.',
                'Never harvest wet tubers from a blighted field; post-harvest breakdown in storage will be catastrophic.'
            ]
        },
        'recovery_monitoring': [
            'Inspect field every 48 hours following systemic application: white sporulation on leaf undersides must vanish completely and lesions must dry into papery brown tissue.',
            'Inspect harvested tubers after 2 weeks in dark, well-ventilated curing storage for brown subsurface rot.'
        ],
        'prevention_next_cycle': [
            'Plant ONLY certified disease-free seed tubers with official late blight inspection certificates.',
            'Select resistant cultivars possessing multi-genic late blight resistance (e.g. Defender, Sarpo Mira, Jacqueline Lee, Kufri Girdhari).',
            'Use predictive Late Blight Decision Support Systems (e.g. BlightCast, Simcast).'
        ],
        'expert_assistance': 'MANDATORY: Report suspected late blight immediately to university extension pathologists or ICAR-CPRI / national agricultural departments to track clonal strains.',
        'references': [
            {'title': 'Potato Late Blight Management', 'source': 'University of Wisconsin Extension Vegetable Pathology', 'url': 'https://vegpath.plantpath.wisc.edu/'},
            {'title': 'USABlight: Late Blight Decision Support System', 'source': 'USDA / National Late Blight Consortium', 'url': 'https://usablight.org/'}
        ]
    },
    'Potato___healthy': {
        'crop': 'Potato',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Vigorous upright dark green compound foliage with smooth, flat leaflets, intact leaf margins, robust stems, and complete absence of target spots, water-soaked blights, or leaf roll.',
        'immediate_actions': ['Maintain weekly field disease scouting through row closure and tuber bulking.'],
        'spread_prevention': ['Monitor for Colorado potato beetle and aphid vectors of Potato Virus Y (PVY).'],
        'cultural_management': [
            'Maintain steady soil moisture at 65-80% available water capacity to prevent tuber cracking and common scab.',
            'Hill soil properly to keep tuber stolons covered from sunlight.'
        ],
        'treatment_options': {
            'cultural': ['Timely hilling and balanced fertigation based on petiole nitrate tests.'],
            'biological': ['Conserve ground beetles and predatory damsel bugs that feed on beetle larvae.'],
            'chemical': ['No curative treatment needed. Maintain preventive protectant cover sprays during regional late blight warnings.'],
            'warnings': ['Avoid excess nitrogen late in the season, which delays tuber skin set and harvest maturity.']
        },
        'recovery_monitoring': ['Monitor canopy senescence timing and tuber skin maturation.'],
        'prevention_next_cycle': ['Continue 3-year crop rotation with non-solanaceous crops.'],
        'expert_assistance': 'Not required for healthy potato fields.',
        'references': [{'title': 'Commercial Potato Production in North America', 'source': 'Potato Association of America Handbook', 'url': 'https://potatoassociation.org/'}]
    },
    'Raspberry___healthy': {
        'crop': 'Raspberry',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Crisp, bright green trifoliate or pentafoliate leaves with silvery undersides, strong primocane and floricane development, and absence of cane blight, rust, or anthracnose spotting.',
        'immediate_actions': ['Maintain routine canopy inspection.'],
        'spread_prevention': ['Inspect cane bases for cane borer swellings or spur blight lesions.'],
        'cultural_management': [
            'Maintain trellis wire support to keep canes upright and well ventilated.',
            'Prune out spent floricanes immediately after summer harvest at ground level to improve airflow.',
            'Maintain soil pH at 6.0 - 6.5 with organic mulch.'
        ],
        'treatment_options': {
            'cultural': ['Remove weak primocanes to keep density at 4-5 canes per linear foot of row.'],
            'biological': ['Conserve beneficial mites and native bee pollinators.'],
            'chemical': ['No curative treatment needed.'],
            'warnings': ['Avoid overhead watering that encourages fruit rot (Botrytis cinerea).']
        },
        'recovery_monitoring': ['Track primocane height and floricane fruit set.'],
        'prevention_next_cycle': ['Perform dormant sanitation pruning of broken or diseased canes.'],
        'expert_assistance': 'Not required for healthy raspberries.',
        'references': [{'title': 'Raspberry Management Guide', 'source': 'Cornell Cooperative Extension Berry Resources', 'url': 'https://fruit.cornell.edu/berry/'}]
    },
    'Soybean___healthy': {
        'crop': 'Soybean',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Uniform deep green trifoliate leaves, robust nodulation on root systems, strong stem branching, and complete absence of frogeye spots, sudden death syndrome chlorosis, or rust pustules.',
        'immediate_actions': ['Continue standard field scouting across V and R developmental stages.'],
        'spread_prevention': ['Clean combine headers before moving from weedy or cyst nematode-infested fields.'],
        'cultural_management': [
            'Ensure effective rhizobial nodulation: check root nodules (healthy nodules show active pink/red leghemoglobin centers).',
            'Scout for soybean aphids at R1-R3 stages.'
        ],
        'treatment_options': {
            'cultural': ['Standard narrow-row planting and integrated weed management.'],
            'biological': ['Conserve predatory pirate bugs (Orius) that consume soybean aphids.'],
            'chemical': ['No curative chemical treatment needed.'],
            'warnings': ['Avoid prophylactic fungicide-insecticide tank mixes that accelerate insect resistance.']
        },
        'recovery_monitoring': ['Monitor pod development at R3-R4 and seed fill at R5-R6.'],
        'prevention_next_cycle': ['Rotate with corn or sorghum to disrupt soybean cyst nematode cycles.'],
        'expert_assistance': 'Not required for healthy soybeans.',
        'references': [{'title': 'Soybean Disease Management', 'source': 'Crop Protection Network / Land-Grant University Extension', 'url': 'https://cropprotectionnetwork.org/'}]
    },
    'Squash___Powdery_mildew': {
        'crop': 'Squash',
        'condition': 'Powdery Mildew (Podosphaera xanthii)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Podosphaera xanthii (syn. Sphaerotheca fuliginea) and Erysiphe cichoracearum',
        'severity': 'Moderate to High',
        'symptoms': 'White, talcum-powder-like fungal patches developing first on the undersides of older crown leaves and shaded petioles; spreads to upper leaf surfaces, causing leaves to turn chlorotic, senesce prematurely, and desiccate, leading to sunburned fruit and reduced yields.',
        'immediate_actions': [
            'Check both upper AND lower surfaces of crown leaves; powdery mildew often begins hidden on lower shaded leaf surfaces.',
            'Determine crop maturity: treatment is critical before fruit enlargement is complete to maintain canopy cover.'
        ],
        'spread_prevention': [
            'Fungal conidia are easily wind-dispersed; avoid excessive mechanical traffic through infected fields when leaves are dry.',
            'Plow under or compost squash vines immediately after harvest to stop airborne spore production.'
        ],
        'cultural_management': [
            'Plant powdery mildew-resistant (PMR) squash and pumpkin cultivars.',
            'Ensure adequate plant spacing (wide rows) to improve air circulation and sunlight penetration.',
            'Avoid excessive nitrogen fertilization that encourages dense, succulent, shaded foliar growth.'
        ],
        'treatment_options': {
            'cultural': ['Plant resistant hybrids; widen vine spacing; avoid excessive nitrogen.'],
            'biological': [
                'Potassium bicarbonate (e.g. MilStop, Armicarb) sprays applied at 7-day intervals to disrupt fungal cell walls.',
                'Horticultural oils or neem seed extracts (e.g. Trilogy) applied thoroughly to leaf undersides.',
                'Bacillus amyloliquefaciens (e.g. Serenade, DoubleNickel) organic bio-fungicides.'
            ],
            'chemical': [
                'Systemic fungicides: Quinoxyfen (FRAC 13), Cyflufenamid (FRAC U06), Metrafenone (FRAC 50), or Penthiopyrad (FRAC 7).',
                'Protectant tank-mix partners: Sulfur (FRAC M02) or Chlorothalonil (FRAC M05) tank-mixed with systemics.',
                'Fungicide Resistance Warning: Podosphaera xanthii has high risk of developing resistance. Many strains are resistant to FRAC 1 (benzimidazoles) and FRAC 11 (strobilurins). Never use solo strobilurins.'
            ],
            'warnings': [
                'Sulfur Phytotoxicity: DO NOT apply sulfur on sulfur-sensitive cucurbit varieties or when temperatures exceed 32°C (90°F).',
                'Observe Pre-Harvest Intervals (PHI) on squash fruit harvested daily.'
            ]
        },
        'recovery_monitoring': [
            'Inspect newly emerging leaves 7-10 days following treatment; new canopy growth should remain deep green without white powdery colonies.',
            'Existing white patches on older leaves should turn brown, dry out, and cease sporulation.'
        ],
        'prevention_next_cycle': [
            'Select PMR squash hybrids with intermediate or high resistance (e.g. Dunja, Cheetah, Green Machine for zucchini; Honeyboat, Metro for winter squash).',
            'Commence scouting early in the season when the earliest fruit begins to set.'
        ],
        'expert_assistance': 'Consult vegetable extension specialists if powdery mildew establishes despite a regular FRAC-rotated fungicide program.',
        'references': [
            {'title': 'Cucurbit Powdery Mildew Management', 'source': 'Cornell Cooperative Extension Vegetable MD Online', 'url': 'http://vegetablemdonline.ppath.cornell.edu/factsheets/Cucurbits_PM.htm'},
            {'title': 'UC IPM: Cucurbits Powdery Mildew', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/cucurbits/powdery-mildew/'}
        ]
    },
    'Strawberry___Leaf_scorch': {
        'crop': 'Strawberry',
        'condition': 'Strawberry Leaf Scorch (Diplocarpon earlianum)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Diplocarpon earlianum (anamorph Marssonia fragariae)',
        'severity': 'Moderate',
        'symptoms': 'Numerous small, irregular, purple-to-dark reddish-brown spots without white centers (distinguishing scorch from common leaf spot); spots coalesce, causing leaves to turn purple or brown and curl upward at the margins, appearing burned or scorched.',
        'immediate_actions': [
            'Inspect planting beds and rogue severely scorched outer leaves during routine maintenance.',
            'Switch from overhead sprinklers to drip irrigation to avoid leaf wetness.'
        ],
        'spread_prevention': [
            'Avoid working in strawberry beds while plants are wet with morning dew.',
            'Renovate strawberry beds promptly after harvest by mowing and removing old diseased foliar residue.'
        ],
        'cultural_management': [
            'Plant strawberries in well-drained, raised beds with full sun exposure.',
            'Maintain proper plant spacing (prevent matted-row over-crowding) to facilitate rapid canopy drying.',
            'Do not apply excessive nitrogen fertilizer in early spring.'
        ],
        'treatment_options': {
            'cultural': [
                'Post-harvest bed renovation: mow old leaves above crowns and till in plant debris.',
                'Drip irrigation under plastic mulch.'
            ],
            'biological': [
                'Copper-based bactericides/fungicides (FRAC M01) applied early in the spring before bloom provides protectant suppression.'
            ],
            'chemical': [
                'Protectant fungicides: Captan (FRAC M04) or Thiram (FRAC M03) applied from new spring growth through harvest.',
                'Systemic fungicides: QoI strobilurins (e.g. Pyraclostrobin - FRAC 11) or DMI triazoles where labeled.'
            ],
            'warnings': [
                'Observe Pre-Harvest Intervals (Captan PHI is typically 0 days, but worker Re-Entry Interval is 24-48 hours).',
                'Avoid applying fungicides during active bee pollination.'
            ]
        },
        'recovery_monitoring': [
            'Check newly emerged trifoliate leaves from the crown 10-14 days post-treatment; new leaves should be uniform emerald green without purplish flecks.',
            'Verify that runner plants establish clean, unspotted root crowns.'
        ],
        'prevention_next_cycle': [
            'Purchase certified disease-free strawberry bare-root or plug plants from registered nurseries.',
            'Select cultivars with moderate to high resistance to leaf scorch (e.g. Allstar, Earliglow, Tribute, Tristar).'
        ],
        'expert_assistance': 'Consult a small fruit extension specialist if scorch lesions spread to fruit calyxes (sepals), causing dry brown fruit caps.',
        'references': [
            {'title': 'Leaf Scorch of Strawberry', 'source': 'Ohio State University Extension FactSheet', 'url': 'https://ohioline.osu.edu/factsheet/plpath-fru-34'},
            {'title': 'UC IPM: Strawberry Leaf Scorch', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/strawberry/leaf-scorch/'}
        ]
    },
    'Strawberry___healthy': {
        'crop': 'Strawberry',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Vibrant, dark green trifoliate leaves with serrated margins, clean crowns, vigorous runner production, and complete absence of purple scorch flecks, angular spots, or gray mold.',
        'immediate_actions': ['Maintain regular strawberry bed monitoring.'],
        'spread_prevention': ['Scout for two-spotted spider mites on leaf undersides and strawberry root weevils.'],
        'cultural_management': [
            'Maintain steady drip irrigation under plastic mulch to prevent moisture stress during fruiting.',
            'Maintain straw mulch around plants to keep berries off bare soil.'
        ],
        'treatment_options': {
            'cultural': ['Remove dead runner foliage and thin crowded crowns.'],
            'biological': ['Release or conserve Neoseiulus californicus or Phytoseiulus persimilis predatory mites.'],
            'chemical': ['No curative chemical treatment needed.'],
            'warnings': ['Avoid over-irrigation that leads to Phytophthora crown rot and red stele.']
        },
        'recovery_monitoring': ['Track blossom set, fruit expansion, and crown runner vigor.'],
        'prevention_next_cycle': ['Rotate strawberry beds every 3-4 years to break soil-borne pathogen cycles.'],
        'expert_assistance': 'Not required for healthy strawberries.',
        'references': [{'title': 'Strawberry Production Guide', 'source': 'North Carolina State University Extension', 'url': 'https://strawberries.ces.ncsu.edu/'}]
    },
    'Tomato___Bacterial_spot': {
        'crop': 'Tomato',
        'condition': 'Bacterial Spot (Xanthomonas spp.)',
        'is_healthy': False,
        'pathogen_type': 'Bacterial',
        'causal_agent': 'Xanthomonas perforans, X. vesicatoria, X. euvesicatoria, and X. gardneri',
        'severity': 'High',
        'symptoms': 'Small, dark brown to black, water-soaked, circular to angular spots on leaves, often surrounded by yellow halos; spots coalesce causing leaf blight and scorch; fruit displays raised, dark, scab-like warty spots with rough margins.',
        'immediate_actions': [
            'DO NOT enter or cultivate tomato fields when foliage is wet from morning dew or rain; bacterial cells easily spread on workers and tools.',
            'Immediately isolate infected greenhouse transplant trays; discard infected flats to prevent greenhouse-wide epidemic.'
        ],
        'spread_prevention': [
            'Sterilize trellising stakes, pruning shears, and plastic clips with 10% bleach or quaternary ammonium between seasons.',
            'Switch completely to drip irrigation under plastic mulch; eliminate overhead sprinkler watering.'
        ],
        'cultural_management': [
            'Enforce a 2-3 year crop rotation away from solanaceous crops (tomato, pepper, potato, eggplant).',
            'Purchase certified pathogen-free seed or perform hot-water seed treatment (50°C for 25 minutes for tomato seed).',
            'Destroy or incorporate tomato vine residue deeply into soil immediately following final harvest.'
        ],
        'treatment_options': {
            'cultural': [
                'Hot-water treated certified seeds.',
                'Drip irrigation and raised plastic mulch beds.',
                'Sanitation of field stakes and machinery.'
            ],
            'biological': [
                'Bacteriophages (AgriPhage Tomato) applied in the late afternoon/evening.',
                'Bacillus amyloliquefaciens (DoubleNickel, Serenade) bio-bactericide sprays.'
            ],
            'chemical': [
                'FUNGICIDES ARE INEFFECTIVE: This is a bacterial disease.',
                'Bactericides: Fixed copper (FRAC M01, e.g. Copper hydroxide, Copper octanoate) TANK-MIXED with Mancozeb (FRAC M03). The tank-mix reaction releases free cupric ions that overcome copper tolerance in Xanthomonas.',
                'Systemic Acquired Resistance (SAR) activators: Acibenzolar-S-methyl (Actigard - FRAC P01) applied preventively every 7-10 days.'
            ],
            'warnings': [
                'Pure copper sprays without mancozeb or SAR activators frequently fail due to widespread copper resistance in Xanthomonas populations.',
                'Observe statutory Pre-Harvest Intervals (Mancozeb PHI is 5 days on fresh market tomato in most jurisdictions).'
            ]
        },
        'recovery_monitoring': [
            'Inspect newly emerging terminal leaflets 7-10 days post-treatment: new foliage should emerge clean and free of water-soaked spots.',
            'Examine expanding green fruit: fruit set after treatment should remain completely smooth and free of warty black scabs.'
        ],
        'prevention_next_cycle': [
            'Select tomato hybrids possessing multi-gene resistance to Xanthomonas races where commercially available.',
            'Implement rigorous greenhouse seedling inspection before field transplanting.'
        ],
        'expert_assistance': 'Consult your local extension vegetable pathologist or KVK specialist if bacterial spot spreads aggressively in hot, wet weather.',
        'references': [
            {'title': 'Bacterial Spot of Tomato', 'source': 'University of Florida IFAS Extension', 'url': 'https://edis.ifas.ufl.edu/publication/VH056'},
            {'title': 'Tomato Bacterial Spot Management', 'source': 'Cornell Cooperative Extension Vegetable MD Online', 'url': 'http://vegetablemdonline.ppath.cornell.edu/'}
        ]
    },
    'Tomato___Early_blight': {
        'crop': 'Tomato',
        'condition': 'Early Blight (Alternaria linariae / A. solani)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Alternaria linariae (formerly A. solani on tomato)',
        'severity': 'Moderate to High',
        'symptoms': 'Brown to black circular spots developing distinctive concentric target-like rings on older leaves first; leaf yellowing and dieback advancing from the ground upward; sunken leathery lesions on fruit stems and calyx ends.',
        'immediate_actions': [
            'Prune and remove severely infected lower leaves up to 30-45 cm (12-18 inches) above the ground; bag and dispose of diseased clippings away from the field.',
            'Ensure plants are staked and trellised off bare soil.'
        ],
        'spread_prevention': [
            'Install plastic mulch or thick organic straw mulch around the base of plants to create a barrier preventing soil splash of fungal spores.',
            'Avoid overhead sprinkler watering; use drip lines exclusively.'
        ],
        'cultural_management': [
            'Stake, cage, or string-trellis tomato vines to keep foliage elevated and promote rapid airflow and sunlight penetration.',
            'Prune lower suckers to maintain open canopy ventilation.',
            'Maintain steady nitrogen fertility; avoid under-fertilizing plants during heavy fruit loading.'
        ],
        'treatment_options': {
            'cultural': [
                'Pruning lower canopy foliage up to 30 cm.',
                'Staking and trellising plants off the ground.',
                'Soil mulching with black plastic or organic straw.'
            ],
            'biological': [
                'Bacillus amyloliquefaciens (DoubleNickel) or Bacillus subtilis (Serenade) applied preventively at early vegetative stages.',
                'Copper octanoate or copper sulfate formulations.'
            ],
            'chemical': [
                'Protectant fungicides: Chlorothalonil (FRAC M05) or Mancozeb (FRAC M03) applied preventively on a 7-10 day schedule.',
                'Systemic fungicides: SDHI fungicides (e.g. Boscalid, Fluxapyroxad - FRAC 7), DMI triazoles (e.g. Difenoconazole - FRAC 3), or Cyprodinil + Fludioxonil (Switch - FRAC 9 + 12).',
                'Strobilurin Warning: Many Alternaria populations have developed resistance to QoI (FRAC 11) fungicides (e.g. Azoxystrobin); do NOT use solo strobilurins.'
            ],
            'warnings': [
                'Chlorothalonil has a 0-day Pre-Harvest Interval on tomato, but strictly observe the 12-hour Re-Entry Interval (REI).',
                'Always alternate FRAC codes to prevent resistant fungal strains from dominating.'
            ]
        },
        'recovery_monitoring': [
            'Inspect mid-canopy leaves 7-10 days after pruning and treatment: the upward advance of yellowing and target spots should be completely halted.',
            'Existing target lesions should dry into brittle, non-expanding brown tissue.'
        ],
        'prevention_next_cycle': [
            'Plant tomato varieties with genetic resistance to early blight (e.g. Defiant PhR, Mountain Merit, Mountain Fresh Plus, Plum Regal, Iron Lady).',
            'Rotate away from nightshade crops (potato, eggplant, pepper) for at least 2-3 years.'
        ],
        'expert_assistance': 'Consult agricultural extension agents if target lesions spread into the upper canopy before the first cluster ripens.',
        'references': [
            {'title': 'Early Blight of Tomato', 'source': 'NC State Extension Plant Pathology', 'url': 'https://content.ces.ncsu.edu/early-blight-of-tomato'},
            {'title': 'UC IPM: Tomato Early Blight', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/tomato/early-blight/'}
        ]
    },
    'Tomato___Late_blight': {
        'crop': 'Tomato',
        'condition': 'Late Blight (Phytophthora infestans)',
        'is_healthy': False,
        'pathogen_type': 'Oomycete (Water Mold)',
        'causal_agent': 'Phytophthora infestans (Oomycete)',
        'severity': 'Critical / Epidemic Hazard',
        'symptoms': 'Rapidly expanding, pale green to water-soaked dark brown or purplish-black lesions on leaves and stems; white, cottony downy sporulation on the underside of leaves during cool, humid morning hours; brown, greasy, firm, leathery rot on green and ripe fruit; total vine collapse.',
        'immediate_actions': [
            'HIGH EPIDEMIC ALERT: Late blight can decimate entire tomato plantings in 5-7 days under cool, wet conditions (15-22°C, >90% RH).',
            'Rogue and remove severely infected plants immediately: bag plants in plastic bags on a sunny day to solarize sporangia, then deep bury or destroy.',
            'Notify neighboring growers and extension agents immediately.'
        ],
        'spread_prevention': [
            'Never compost late-blight infected tomato vines in open compost piles; spores travel miles on wind currents.',
            'Eliminate all volunteer tomatoes and potato cull piles nearby.'
        ],
        'cultural_management': [
            'Maintain maximum plant spacing and high staking to ensure maximum sunlight penetration and wind drying.',
            'Use drip irrigation exclusively; never use overhead sprinklers.',
            'Avoid working in wet fields.'
        ],
        'treatment_options': {
            'cultural': [
                'Immediate removal and bagging of infected plants.',
                'Strict eradication of volunteer potatoes and tomatoes in proximity.'
            ],
            'biological': [
                'Fixed copper formulations (FRAC M01) provide protectant suppression in certified organic crops, but CANNOT rescue plants once internal infection begins.'
            ],
            'chemical': [
                'CRITICAL PATHOGEN NOTE: Phytophthora infestans is an OOMYCETE, NOT a fungus. Standard fungal sprays (e.g. strobilurins alone, myclobutanil) are completely useless.',
                'Protectants: Chlorothalonil (FRAC M05) or Mancozeb (FRAC M03) applied prior to infection.',
                'Specialized Oomycete-targeted systemics: Mandipropamid (Revus - FRAC 40), Cyazofamid (Ranman - FRAC 21), Fluopicolide (Presidio - FRAC 43), Cymoxanil (Curzate - FRAC 27, kickback activity), or Propamocarb (Previcur Flex - FRAC 28).',
                'Mefenoxam (Ridomil) Warning: Many current Phytophthora lineages (e.g. US-23) may tolerate or resist mefenoxam; consult local diagnostic labs before using.'
            ],
            'warnings': [
                'Under favorable weather (cool, overcast, raining), spray intervals must be tightened to 5-7 days.',
                'Strictly adhere to Pre-Harvest Intervals on picking fruit.'
            ]
        },
        'recovery_monitoring': [
            'Inspect remaining plants every 48 hours: white downy sporulation on leaf undersides must vanish completely and lesions must dry into papery, crisp dead tissue.',
            'Check green tomato fruit daily for greasy brown shoulders.'
        ],
        'prevention_next_cycle': [
            'Plant late-blight resistant tomato cultivars containing both Ph-2 and Ph-3 resistance genes (e.g. Mountain Merit, Defiant PhR, Iron Lady, Plum Regal, Mountain Magic).',
            'Subscribe to regional late blight warning alerts (e.g. USABlight, BlightCast).'
        ],
        'expert_assistance': 'MANDATORY: Report suspected late blight immediately to university extension pathologists or local KVK scientists for strain genotyping.',
        'references': [
            {'title': 'Late Blight on Tomato', 'source': 'Cornell Cooperative Extension Vegetable MD Online', 'url': 'http://vegetablemdonline.ppath.cornell.edu/factsheets/Tomato_LateBlight.htm'},
            {'title': 'Late Blight Management in Tomato', 'source': 'University of Florida IFAS Extension', 'url': 'https://edis.ifas.ufl.edu/publication/PP301'}
        ]
    },
    'Tomato___Leaf_Mold': {
        'crop': 'Tomato',
        'condition': 'Tomato Leaf Mold (Passalora fulva)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Passalora fulva (syn. Cladosporium fulvum)',
        'severity': 'Moderate (High in High-Tunnels / Greenhouses)',
        'symptoms': 'Pale green to bright yellowish chlorotic spots on the upper leaf surface with indistinct margins; olive-green, brown, to velvety grayish-purple fungal mold sporulation on the corresponding underside of the leaf; leaves curl, wither, and drop prematurely.',
        'immediate_actions': [
            'VENTILATE IMMEDIATELY: If growing in high tunnels or greenhouses, open side curtains, ridge vents, and run horizontal airflow fans to drop relative humidity below 85%.',
            'Prune and destroy severely molded lower leaves to remove fungal inoculum.'
        ],
        'spread_prevention': [
            'Keep relative humidity strictly below 85%; Passalora fulva spores CANNOT germinate below 85% RH.',
            'Switch from any overhead watering to drip irrigation; avoid splashing water on foliage.'
        ],
        'cultural_management': [
            'Maintain wide spacing between plants and stake vertically to open canopy airflow.',
            'Prune lower suckers and foliage up to the lowest fruit cluster to increase air movement at the ground level.',
            'Heat and ventilate high tunnels in late afternoon to prevent condensation on leaves during cool nights.'
        ],
        'treatment_options': {
            'cultural': [
                'Aggressive greenhouse ventilation to maintain RH < 85%.',
                'Pruning lower foliage and drip irrigation.'
            ],
            'biological': [
                'Bio-fungicides: Bacillus amyloliquefaciens (DoubleNickel) or Bacillus subtilis (Serenade) applied preventively.',
                'Copper sulfate or copper octanoate formulations.'
            ],
            'chemical': [
                'Protectants: Chlorothalonil (FRAC M05) or Mancozeb (FRAC M03) applied at first sign of lower leaf spotting.',
                'Systemic fungicides: Difenoconazole + Cyprodinil (Inspire Super - FRAC 3 + 9), Cyazofamid, or Boscalid (FRAC 7).'
            ],
            'warnings': [
                'Many protectant fungicides have specific greenhouse restrictions; verify that the product label explicitly permits greenhouse/high-tunnel application.',
                'Adhere to Re-Entry Intervals and use appropriate PPE inside enclosed structures.'
            ]
        },
        'recovery_monitoring': [
            'Inspect leaf undersides 7-10 days following ventilation and spray treatments: velvety olive sporulation should disappear and leave dry, inactive tan spots.',
            'Scout upper canopy leaves to confirm that no new yellow patches emerge.'
        ],
        'prevention_next_cycle': [
            'Plant leaf-mold resistant tomato hybrids carrying Cf resistance genes (Cf-2, Cf-4, Cf-5, Cf-9, e.g. Geronimo, Rebelski, Foronti, Trust).',
            'Thoroughly steam-clean, wash, or disinfect greenhouse structures and ground covers between crop cycles.'
        ],
        'expert_assistance': 'Contact a greenhouse vegetable specialist if leaf mold persists despite relative humidity being maintained below 85%.',
        'references': [
            {'title': 'Tomato Leaf Mold in High Tunnels', 'source': 'University of Minnesota Extension', 'url': 'https://extension.umn.edu/disease-management/tomato-leaf-mold'},
            {'title': 'UC IPM: Tomato Leaf Mold', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/tomato/leaf-mold/'}
        ]
    },
    'Tomato___Septoria_leaf_spot': {
        'crop': 'Tomato',
        'condition': 'Septoria Leaf Spot (Septoria lycopersici)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Septoria lycopersici',
        'severity': 'Moderate to High',
        'symptoms': 'Numerous small (1.5 - 3 mm), circular, water-soaked spots developing dark brown margins and sunken grayish-white centers; tiny, black, pimple-like pycnidia (spore fruiting bodies) clearly visible inside the gray lesion center with a hand lens; severe defoliation advances rapidly from the bottom of the plant upward.',
        'immediate_actions': [
            'Prune and destroy infected lower leaves displaying dense Septoria spotting; bag clippings immediately.',
            'Confirm lesion anatomy with a 10x hand lens: black pycnidia pimples in gray centers confirm Septoria (distinguishing it from bacterial spot or early blight).'
        ],
        'spread_prevention': [
            'Apply thick straw mulch or black plastic mulch under plants to eliminate soil splash from rain.',
            'Do NOT cultivate, prune, or harvest when tomato vines are wet.'
        ],
        'cultural_management': [
            'Stake, cage, or string-trellis plants to keep foliage elevated off wet ground.',
            'Enforce a strict 2 to 3-year crop rotation away from solanaceous plants.',
            'Eradicate solanaceous weeds (e.g. horsenettle, black nightshade) which serve as wild reservoirs.'
        ],
        'treatment_options': {
            'cultural': [
                'Bottom-leaf pruning up to 30 cm.',
                'Staking and trellising for canopy ventilation.',
                'Ground mulching with clean straw or plastic.'
            ],
            'biological': [
                'Bacillus subtilis or Bacillus amyloliquefaciens organic formulations applied preventively at early bloom.',
                'Fixed copper formulations (FRAC M01) applied as protectants.'
            ],
            'chemical': [
                'Protectants: Chlorothalonil (FRAC M05) or Mancozeb (FRAC M03) applied preventively every 7-10 days once lower leaves touch the ground.',
                'Systemic options: DMI triazoles (e.g. Difenoconazole - FRAC 3) or SDHI fungicides (e.g. Boscalid - FRAC 7).',
                'Strobilurin Warning: Rotate FRAC 11 (Azoxystrobin, Pyraclostrobin) with FRAC M05 or FRAC 3; do not make more than 2 sequential FRAC 11 applications.'
            ],
            'warnings': [
                'Adhere to Pre-Harvest Intervals (Mancozeb PHI is 5 days on fresh market tomato).',
                'Wear protective gloves and long sleeves during pruning and spraying.'
            ]
        },
        'recovery_monitoring': [
            'Inspect newly emerging upper canopy leaves 7-10 days following treatment: new leaves must remain spotless and vibrant green.',
            'Confirm that lower defoliation has halted below the primary fruit clusters.'
        ],
        'prevention_next_cycle': [
            'Plant tomato varieties with high tolerance or partial resistance to foliar blights (e.g. Mountain Supreme, Mountain Fresh Plus, Iron Lady).',
            'Till under or compost crop residues deeply immediately after final harvest.'
        ],
        'expert_assistance': 'Consult your local extension vegetable specialist if Septoria defoliation reaches the middle canopy before fruit begins ripening.',
        'references': [
            {'title': 'Septoria Leaf Spot of Tomato', 'source': 'University of Missouri Extension', 'url': 'https://extension.missouri.edu/publications/g6202'},
            {'title': 'Tomato Septoria Leaf Spot Management', 'source': 'Penn State Extension', 'url': 'https://extension.psu.edu/septoria-leaf-spot-on-tomato'}
        ]
    },
    'Tomato___Spider_mites Two-spotted_spider_mite': {
        'crop': 'Tomato',
        'condition': 'Two-Spotted Spider Mite (Tetranychus urticae)',
        'is_healthy': False,
        'pathogen_type': 'Arachnid Pest / Mite',
        'causal_agent': 'Tetranychus urticae (Two-Spotted Spider Mite, Acari: Tetranychidae)',
        'severity': 'High (Under Hot, Dry Conditions)',
        'symptoms': 'Fine pale yellow or white stippling (pinpoint speckling) on the upper leaf surface; fine silky webbing visible on leaf undersides, growing tips, and floral clusters; leaves turn chlorotic, bronze, desiccate, and drop; fruit develops speckled russeting.',
        'immediate_actions': [
            'INSPECT WITH HAND LENS: Confirm presence of tiny oval mites with two dark lateral body spots and tiny spherical translucent eggs on leaf undersides.',
            'CRITICAL WARNING: DO NOT APPLY BROAD-SPECTRUM SYNTHETIC PYRETHROIDS OR CARBARYL. These chemicals kill beneficial predatory mites and cause explosive spider mite population flare-ups.'
        ],
        'spread_prevention': [
            'Suppress dust: keep field access roads watered or oiled; dusty conditions severely aggravate spider mite infestations.',
            'Overhead misting or water washing of lower leaf surfaces can physically knock down mite populations in small plots.'
        ],
        'cultural_management': [
            'Avoid plant water stress: drought-stressed tomato plants are highly preferred by spider mites and trigger rapid mite reproduction.',
            'Remove and destroy heavily infested, heavily webbed plants ("hot-spots") before mites migrate along wind currents.'
        ],
        'treatment_options': {
            'cultural': [
                'Dust control on surrounding dirt roads.',
                'Maintaining optimal plant hydration to reduce host attractiveness.',
                'Physical rogueing of severely webbed hot-spot plants.'
            ],
            'biological': [
                'Biological predators: Release predatory mites (Phytoseiulus persimilis, Neoseiulus californicus, or Galendromus occidentalis) at early low-density mite onset.',
                'Foliar bio-pesticides: Insecticidal soap (potassium salts of fatty acids) or horticultural narrow-range mineral oil applied with high pressure to coat leaf undersides.',
                'Neem-derived Azadirachtin or Beauveria bassiana entomopathogenic fungus.'
            ],
            'chemical': [
                'FUNGICIDES DO NOT KILL MITES: This is an arachnid arthropod pest. Applying fungicides has ZERO effect on spider mites.',
                'Selective Miticides: Bifenazate (Acramite - IRAC 20D), Spiromesifen (Oberon - IRAC 23), Abamectin (Agri-Mek - IRAC 6), or Etoxazole (Zeal - IRAC 10B).',
                'Coverage: Miticide sprays MUST be applied with high water volume and drop nozzles to thoroughly wet leaf undersides where mites colonize.'
            ],
            'warnings': [
                'Rotate IRAC modes of action strictly; Tetranychus urticae evolves resistance faster than almost any other agricultural pest.',
                'Observe Pre-Harvest Intervals (Abamectin PHI is typically 7 days; Bifenazate PHI is 3 days on tomato).'
            ]
        },
        'recovery_monitoring': [
            'Scout leaf undersides with a 10-14x hand lens 3-5 days post-miticide treatment: adult mites should be dead/immobile.',
            'Inspect newly developing terminal leaves: new growth should be free of yellow stippling and webbing.'
        ],
        'prevention_next_cycle': [
            'Clean and sanitize greenhouse benches and high-tunnel frames with soap or bleach between seasons.',
            'Eliminate broadleaf weeds (e.g. mallow, pigweed, bindweed) around field borders that harbor overwintering female mites.'
        ],
        'expert_assistance': 'Consult agricultural entomology extension specialists if miticides fail or webbed colonies spread rapidly.',
        'references': [
            {'title': 'Two-Spotted Spider Mite Management on Tomato', 'source': 'University of Florida IFAS Extension', 'url': 'https://edis.ifas.ufl.edu/publication/IN307'},
            {'title': 'UC IPM: Spider Mites on Tomato', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/tomato/spider-mites/'}
        ]
    },
    'Tomato___Target_Spot': {
        'crop': 'Tomato',
        'condition': 'Target Spot (Corynespora cassiicola)',
        'is_healthy': False,
        'pathogen_type': 'Fungal',
        'causal_agent': 'Corynespora cassiicola',
        'severity': 'Moderate to High',
        'symptoms': 'Small, pinpoint brown spots on leaves enlarging into circular lesions with light brown centers and dark brown margins; older lesions display subtle concentric rings resembling targets; lesions on green fruit appear as small, slightly sunken, dark brown flecks with pale halos, expanding into deeply cratered rot.',
        'immediate_actions': [
            'Differentiate from early blight and bacterial spot: target spot lesions are typically circular with uniform concentric zoning and do not follow leaf veins.',
            'Prune off heavily spotted lower leaves and improve canopy ventilation.'
        ],
        'spread_prevention': [
            'Avoid overhead irrigation that extends leaf wetness; keep foliage completely dry during morning hours.',
            'Do not work in fields when leaves are wet.'
        ],
        'cultural_management': [
            'Stake and string-trellis tomato vines to keep all foliage off the ground.',
            'Ensure wide plant spacing to facilitate rapid air drying inside the canopy.',
            'Practice a 2 to 3-year crop rotation with non-host crops (corn, sorghum, grasses; avoid rotating with cotton or soybean which host Corynespora).'
        ],
        'treatment_options': {
            'cultural': [
                'Staking and pruning lower suckers.',
                'Drip irrigation and plastic mulching.',
                'Sanitation of crop debris.'
            ],
            'biological': [
                'Bacillus amyloliquefaciens (DoubleNickel) bio-fungicide applied preventively before disease onset.'
            ],
            'chemical': [
                'Protectants: Chlorothalonil (FRAC M05) or Mancozeb (FRAC M03) applied preventively at early flowering.',
                'Targeted systemics: Boscalid (Endura - FRAC 7), Fluopyram (FRAC 7), or Difenoconazole + Cyprodinil (Inspire Super - FRAC 3 + 9).',
                'Strobilurin Resistance: Corynespora cassiicola strains are frequently resistant to QoI strobilurins (FRAC 11, e.g. Azoxystrobin, Pyraclostrobin); avoid solo strobilurin sprays.'
            ],
            'warnings': [
                'Rotate FRAC classes every single application to prevent rapid selection for SDHI (FRAC 7) resistance.',
                'Observe Pre-Harvest Intervals on fresh market tomatoes.'
            ]
        },
        'recovery_monitoring': [
            'Inspect mid-canopy leaves 7-10 days following treatment: new leaves should remain green and unblemished.',
            'Check green fruit clusters to ensure that sunken brown flecks do not develop.'
        ],
        'prevention_next_cycle': [
            'Incorporate or destroy tomato residues immediately after harvest to stop fungal survival on dead stalks.',
            'Select tolerant varieties and implement preventive protectant programs in warm, humid production zones.'
        ],
        'expert_assistance': 'Consult vegetable extension specialists if fruit lesion cratering causes severe culling at harvest.',
        'references': [
            {'title': 'Target Spot of Tomato', 'source': 'University of Florida IFAS Extension', 'url': 'https://edis.ifas.ufl.edu/publication/PP316'},
            {'title': 'Target Spot Management in Fresh Market Tomato', 'source': 'NC State Extension Plant Pathology', 'url': 'https://content.ces.ncsu.edu/target-spot-of-tomato'}
        ]
    },
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
        'crop': 'Tomato',
        'condition': 'Tomato Yellow Leaf Curl Virus (TYLCV)',
        'is_healthy': False,
        'pathogen_type': 'Viral (Geminiviridae: Begomovirus)',
        'causal_agent': 'Tomato Yellow Leaf Curl Virus (transmitted by Sweetpotato Whitefly, Bemisia tabaci)',
        'severity': 'Critical / Severe Yield Loss',
        'symptoms': 'Severe stunting and dwarfing of the plant; leaves are abnormally small, cupped upward (boat-shaped), with prominent yellowing (chlorosis) along margins and interveinal areas; crinkled leathery texture; flowers abort and drop prematurely, resulting in almost complete failure to set fruit.',
        'immediate_actions': [
            'CRITICAL VIRUS PROTOCOL: Chemical fungicides and bactericides CANNOT cure a viral infection. DO NOT SPRAY FUNGICIDES.',
            'Rogue and remove infected plants immediately: place an opaque plastic bag over the plant to trap adult whiteflies, cut at the base, and dispose of off-site.',
            'Inspect adjacent plants for the vector: Sweetpotato Whitefly (Bemisia tabaci) — tiny white-winged insects resting on the undersides of young terminal leaves.'
        ],
        'spread_prevention': [
            'Vector control: suppress whitefly populations immediately to prevent rapid secondary virus transmission.',
            'Install yellow sticky cards throughout the field or greenhouse to monitor whitefly population dynamics.',
            'In protected culture (high tunnels/greenhouses), cover all vents and doorways with fine 50-mesh (297-micron) insect exclusion netting.'
        ],
        'cultural_management': [
            'Enforce a strict 2-3 month regional tomato-free and pepper-free host break between cropping seasons to starve whitefly-transmitted virus cycles.',
            'Eliminate alternative weed hosts of TYLCV (e.g. nightshades, jimsonweed, cheeseweed, mallow).',
            'Use reflective silver/metallic plastic mulches in open fields, which disorient incoming whiteflies and reduce early virus transmission.'
        ],
        'treatment_options': {
            'cultural': [
                'Immediate rogueing and bagging of infected plants.',
                'Reflective metallic mulch to repel vector whiteflies.',
                '50-mesh insect exclusion screens in greenhouses.'
            ],
            'biological': [
                'Biological control of whiteflies: Release parasitic wasps (Encarsia formosa, Eretmocerus eremicus) or predatory mites (Amblyseius swirskii) in protected culture.',
                'Apply horticultural mineral oils, insecticidal soaps, or Beauveria bassiana entomopathogenic fungus.'
            ],
            'chemical': [
                'ANTIVIRAL NOTE: There are NO commercial antiviral chemical sprays that cure plant viruses.',
                'Vector Insecticides: Systemic neonicotinoids (e.g. Imidacloprid, Dinotefuran - IRAC 4A) applied via drip chemigation at transplanting, or diamides (e.g. Cyantraniliprole - IRAC 28) and lipid synthesis inhibitors (e.g. Spiromesifen - IRAC 23).',
                'Rotate insecticide modes of action to manage rapid whitefly resistance.'
            ],
            'warnings': [
                'DO NOT SPRAY FUNGICIDES: Fungicides will NOT treat viral conditions and represent wasted money and chemical exposure.',
                'Protect bees and pollinators: do not apply systemic insecticides to blooming plants.'
            ]
        },
        'recovery_monitoring': [
            'Infected plants WILL NOT RECOVER; remove them to protect uninfected rows.',
            'Monitor healthy plants: check new flushes for absence of upward leaf cupping and yellow margins.',
            'Track whitefly counts per leaf on yellow sticky cards.'
        ],
        'prevention_next_cycle': [
            'PLANT TYLCV-RESISTANT HYBRIDS: Planting resistant tomato varieties carrying the Ty-1, Ty-3, or Ty-5 resistance genes (e.g. Tygress, Charger, SecuriTY, Mountain Gem, Red Deuce) is the single most effective defense.',
            'Use only certified virus-free transplants produced in certified insect-screened nurseries.'
        ],
        'expert_assistance': 'Contact your local university extension vegetable entomologist or KVK specialist for regional whitefly resistance updates and TYLCV management protocols.',
        'references': [
            {'title': 'Tomato Yellow Leaf Curl Virus Management', 'source': 'University of Florida IFAS Extension', 'url': 'https://edis.ifas.ufl.edu/publication/IN725'},
            {'title': 'UC IPM: Tomato Yellow Leaf Curl', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/tomato/tomato-yellow-leaf-curl/'}
        ]
    },
    'Tomato___Tomato_mosaic_virus': {
        'crop': 'Tomato',
        'condition': 'Tomato Mosaic Virus (ToMV)',
        'is_healthy': False,
        'pathogen_type': 'Viral (Virgaviridae: Tobamovirus)',
        'causal_agent': 'Tomato Mosaic Tobamovirus (ToMV)',
        'severity': 'High (Mechanically Transmitted)',
        'symptoms': 'Mottled alternating light and dark green mosaic patterns on leaves; leaf puckering, distortion, and narrowing (fern-leaf or shoestringing appearance); plant stunting; internal brown necrotic browning (vascular necrosis) inside fruit flesh.',
        'immediate_actions': [
            'CRITICAL VIRUS PROTOCOL: Chemical fungicides and bactericides CANNOT cure a viral infection. DO NOT SPRAY FUNGICIDES.',
            'Rogue and carefully remove infected plants immediately; handle plants gently to avoid mechanical sap transfer to adjacent healthy foliage.',
            'WASH HANDS AND TOOLS IMMEDIATELY: Tobamoviruses are extraordinarily stable and transmitted mechanically on hands, clothing, pruners, and trellising twine.'
        ],
        'spread_prevention': [
            'Disinfect tools and hands: dip hands and pruning shears in a 20% solution of non-fat dry milk or a 10% solution of trisodium phosphate (TSP) or 10% household bleach between plants.',
            'Strictly prohibit tobacco smoking, chewing, or handling near tomato plantings (tobacco products can carry infectious Tobamoviruses).',
            'Avoid brushing against wet plants during routine pruning or harvesting.'
        ],
        'cultural_management': [
            'Use certified virus-tested seeds treated with dry heat (70°C for 2-4 days) or 10% TSP soak to eliminate seed-coat contamination.',
            'Sterilize tomato greenhouse stakes and pots with steam or bleach between crops.',
            'Discard infected plant debris away from agricultural areas; Tobamoviruses survive in dry plant residue for years.'
        ],
        'treatment_options': {
            'cultural': [
                'Immediate rogueing of infected plants.',
                'Milk or TSP disinfectant hand and tool dips during pruning.',
                'Strict tobacco ban in production facilities.'
            ],
            'biological': [
                'Cross-protection (inoculating seedlings with mild attenuated virus strains) is used in specialized commercial greenhouses where certified seed is unavailable.'
            ],
            'chemical': [
                'NO CHEMICAL CURE: Neither fungicides, bactericides, nor insecticides cure Tobamoviruses.',
                'Disinfectants: Trisodium phosphate (TSP), non-fat dry milk, or Virkon-S for surface sanitization of tools, footwear, and greenhouse benches.'
            ],
            'warnings': [
                'DO NOT APPLY CHEMICAL FUNGICIDES OR PESTICIDES. They provide zero efficacy against Tomato Mosaic Virus.',
                'ToMV can persist on wooden stakes and greenhouse walls for multiple seasons if not thoroughly disinfected.'
            ]
        },
        'recovery_monitoring': [
            'Infected plants WILL NOT RECOVER; remove them from production.',
            'Inspect remaining plants 10-14 days post-sanitation: new flushes must show broad, flat, uniform green leaf blades without mosaic mottling or strap-like distortion.'
        ],
        'prevention_next_cycle': [
            'PLANT ToMV-RESISTANT VARIETIES: Select tomato cultivars possessing the Tm-2 or Tm-2^2 resistance alleles (most modern commercial hybrids possess genetic resistance to ToMV).',
            'Purchase certified disease-free seed from reputable commercial distributors.'
        ],
        'expert_assistance': 'Consult agricultural extension plant pathology clinics for ELISA or PCR molecular confirmation to distinguish ToMV from Cucumber Mosaic Virus (CMV) or Tomato Brown Rugose Fruit Virus (ToBRFV).',
        'references': [
            {'title': 'Tomato Mosaic Virus and Tobacco Mosaic Virus', 'source': 'University of Minnesota Extension', 'url': 'https://extension.umn.edu/disease-management/tomato-mosaic-virus-and-tobacco-mosaic-virus'},
            {'title': 'UC IPM: Tomato Mosaic', 'source': 'University of California Statewide IPM', 'url': 'https://ipm.ucanr.edu/agriculture/tomato/tomato-mosaic/'}
        ]
    },
    'Tomato___healthy': {
        'crop': 'Tomato',
        'condition': 'Healthy Foliage',
        'is_healthy': True,
        'pathogen_type': 'Physiological',
        'causal_agent': 'None (Healthy vegetative tissue)',
        'severity': 'None',
        'symptoms': 'Vigorous deep green compound foliage with erect turgor, clean petioles, strong flower clusters, uniform fruit set, and complete absence of necrotic spotting, chlorotic halos, or leaf curling.',
        'immediate_actions': ['Maintain standard weekly vegetable scouting schedule.'],
        'spread_prevention': ['Maintain clean tool sanitation and inspect for early whitefly or hornworm presence.'],
        'cultural_management': [
            'Maintain steady drip irrigation under mulch to prevent blossom end rot and fruit splitting.',
            'Prune lower suckers to maintain canopy airflow and fruit cluster support.'
        ],
        'treatment_options': {
            'cultural': ['Standard trellising, sucker pruning, and balanced N-P-K fertigation.'],
            'biological': ['Conserve beneficial generalist predators (lacewings, ladybugs, predatory bugs).'],
            'chemical': ['No curative chemical treatment needed.'],
            'warnings': ['Avoid over-fertilizing with nitrogen which creates excessive vegetative foliage at the expense of fruit set.']
        },
        'recovery_monitoring': ['Track weekly cluster flowering, fruit diameter expansion, and uniform ripening.'],
        'prevention_next_cycle': ['Rotate with sweet corn, brassicas, or legumes every 2-3 years.'],
        'expert_assistance': 'Not required for healthy tomato plants.',
        'references': [{'title': 'Tomato Production Guide', 'source': 'Penn State Extension Commercial Vegetable Production', 'url': 'https://extension.psu.edu/commercial-tomato-production'}]
    }
}

def get_disease_management(class_name, is_reliable=True, is_compatible=True, investigated_candidate=None):
    """
    Retrieves the structured agronomic disease management guidance for a given class.
    Enforces conditional treatment withholding when prediction is unreliable or species is incompatible.
    When an investigated out-of-distribution candidate is provided (e.g. Maple Tar Spot or Pear Rust),
    provides tailored low-risk cultural guidance and extension references with chemical advice withheld.
    """
    kb = DISEASE_MANAGEMENT_KB.get(class_name)
    if not kb:
        kb = {
            'crop': 'Unsupported Crop',
            'condition': 'Unsupported plant species',
            'is_healthy': False,
            'pathogen_type': 'Unverified',
            'causal_agent': 'Unverified',
            'severity': 'Unverified',
            'symptoms': 'Foliar symptoms unverified on benchmark model.',
            'immediate_actions': [],
            'spread_prevention': [],
            'cultural_management': [],
            'recovery_monitoring': [],
            'prevention_next_cycle': [],
            'expert_assistance': 'Consult a plant pathologist or university extension specialist.',
            'references': [],
            'treatment_options': {'cultural': [], 'biological': [], 'chemical': [], 'warnings': []}
        }

    # Safe clone of entry
    result = {
        'has_kb_entry': True,
        'crop': kb['crop'],
        'condition': kb['condition'],
        'is_healthy': kb['is_healthy'],
        'pathogen_type': kb['pathogen_type'],
        'causal_agent': kb['causal_agent'],
        'severity': kb['severity'],
        'symptoms': kb['symptoms'],
        'immediate_actions': kb['immediate_actions'],
        'spread_prevention': kb['spread_prevention'],
        'cultural_management': kb['cultural_management'],
        'recovery_monitoring': kb['recovery_monitoring'],
        'prevention_next_cycle': kb['prevention_next_cycle'],
        'expert_assistance': kb['expert_assistance'],
        'references': kb['references'],
        'treatment_withheld': not (is_reliable and is_compatible)
    }

    if is_reliable and is_compatible:
        # Full verified treatment options
        result['treatment_options'] = kb['treatment_options']
        result['treatment_withheld'] = False
        result['withheld_reason'] = None
    elif investigated_candidate == 'maple_tar_spot':
        # Investigated candidate profile for Maple Tar Spot (Rhytisma acerinum)
        result['has_kb_entry'] = True
        result['crop'] = 'Maple (Acer spp.)'
        result['condition'] = 'Maple Tar Spot (Rhytisma acerinum) — Investigated Candidate'
        result['pathogen_type'] = 'Fungal (Ascomycete)'
        result['causal_agent'] = 'Rhytisma acerinum / Rhytisma punctatum'
        result['severity'] = 'Low to Moderate (Aesthetic / Premature Leaf Drop)'
        result['symptoms'] = (
            'Prominent, raised circular jet-black stromatic spots resembling tar droplets (up to 1.5 cm diameter) '
            'on upper leaf surfaces, commonly surrounded by chlorotic yellow-green halos.'
        )
        result['immediate_actions'] = [
            'Collect, bag, and discard fallen symptomatic maple leaves beneath the tree canopy.',
            'Do NOT spray agricultural fungicides formulated for agronomic field crops (like corn or grains).',
            'Inspect adjacent maple trees (especially Norway, red, and silver maples) to evaluate severity of foliar spots.'
        ]
        result['spread_prevention'] = [
            'Rake and dispose of fallen maple leaves before winter dormancy to disrupt overwintering apothecia.',
            'Avoid overhead sprinkler irrigation that wets tree leaves during humid morning hours.',
            'Ensure adequate tree spacing to allow natural air movement.'
        ]
        result['cultural_management'] = [
            'Rake and thoroughly compost or destroy fallen maple leaves in late autumn before winter snow cover.',
            'Prune crowded lower branches during winter dormancy to promote rapid leaf drying through improved cross-canopy airflow.',
            'Maintain tree root health with organic mulch around the drip-line, keeping mulch 5 cm away from the trunk.'
        ]
        result['recovery_monitoring'] = [
            'Check new spring foliage for clean green development; initial infection appears as small pale yellow-green spots in late spring before turning black in late summer.',
            'Mature shade trees readily tolerate tar spot infections without long-term vascular or health damage.'
        ]
        result['prevention_next_cycle'] = [
            'Thorough autumn sanitation (removing leaf litter where spores overwinter) is the most effective cultural control.'
        ]
        result['references'] = [
            {'title': 'Tar Spot on Maple — Penn State Extension', 'source': 'Penn State Extension', 'url': 'https://extension.psu.edu/tar-spot-on-maple'},
            {'title': 'Tar Spot on Trees — University of Minnesota Extension', 'source': 'UMN Extension', 'url': 'https://extension.umn.edu/plant-diseases/tar-spot-trees'},
            {'title': 'Tar Spots of Maple — Cornell University Plant Disease Diagnostic Clinic', 'source': 'Cornell University', 'url': 'http://plantclinic.cornell.edu/factsheets/tarspot.pdf'}
        ]
        result['expert_assistance'] = 'Consult an ISA-certified arborist or university plant pathology extension clinic if young saplings experience severe premature defoliation.'
        result['treatment_withheld'] = True
        result['withheld_reason'] = 'Chemical treatment withheld: Tar spot on mature maples is primarily an aesthetic shade-tree condition; chemical fungicides are rarely justified.'
        result['treatment_options'] = {
            'cultural': [
                'Autumn sanitation: Rake, bag, and dispose of fallen symptomatic leaves to interrupt the sexual ascospore cycle.',
                'Canopy thinning: Prune dead and overcrowded branches during dormancy to accelerate foliar drying.'
            ],
            'biological': [
                'Promote natural soil biodiversity and beneficial fungal decomposers in tree root zones.'
            ],
            'chemical': [], # STRICTLY EMPTY
            'warnings': [
                'CHEMICAL SAFEGUARD: Synthetic fungicides are withheld. Chemical spraying is rarely justified for tar spot on mature maples.',
                'Never apply crop fungicides formulated for field crops (like Corn or Soybeans) onto maple trees.',
                'Physical confirmation by a certified arborist or diagnostic clinic is advised before applying any treatment.'
            ]
        }
    elif investigated_candidate == 'pear_rust':
        # Investigated candidate profile for European Pear Rust (Gymnosporangium sabinae)
        result['has_kb_entry'] = True
        result['crop'] = 'Pear (Pyrus spp.)'
        result['condition'] = 'European Pear Rust / Trellis Rust (Gymnosporangium sabinae) — Investigated Candidate'
        result['pathogen_type'] = 'Fungal (Heteroecious Basidiomycete Rust)'
        result['causal_agent'] = 'Gymnosporangium sabinae (teleomorph) / Roestelia cancellata (aecial)'
        result['severity'] = 'Moderate to High (Foliar Spotting and Fruit Blistering)'
        result['symptoms'] = (
            'Brilliant yellow-orange to bright red-orange blister-like pustules on upper pear leaf surfaces in early summer, '
            'developing swollen gall-like projections and tubular aecial cups on the lower leaf surface in late summer.'
        )
        result['immediate_actions'] = [
            'Inspect nearby ornamental juniper and cedar bushes (within 150–500 meters) for swollen galls with orange gelatinous spore horns in spring.',
            'Prune heavily infected small pear twigs bearing swollen cankers.',
            'Do NOT spray field crop or corn fungicides onto fruit trees.'
        ]
        result['spread_prevention'] = [
            'Interrupt the heteroecious rust cycle by eliminating or pruning galled alternate juniper hosts located nearby.',
            'Prune out swollen perennial galls on juniper branches in late winter before warm spring rains trigger spore release.',
            'Rake and dispose of fallen infected pear foliage in autumn.'
        ]
        result['cultural_management'] = [
            'Maintain spatial separation (at least 150–500 meters where feasible) between pear plantings and ornamental junipers.',
            'Perform selective winter dormant pruning on pear trees to maximize canopy ventilation and sunlight penetration.',
            'Avoid overhead sprinkler irrigation; apply irrigation at soil level.'
        ]
        result['recovery_monitoring'] = [
            'Monitor new spring pear leaves for bright yellow-orange flecks starting in May–June.',
            'Inspect junipers in early spring during rainfall for telial spore horns (gelatinous orange tendrils).'
        ]
        result['prevention_next_cycle'] = [
            'Removing galled juniper branches during winter dormancy directly reduces spring basidiospore pressure on pear foliage.'
        ]
        result['references'] = [
            {'title': 'Pear Rust (Gymnosporangium) — Penn State Extension', 'source': 'Penn State Extension', 'url': 'https://extension.psu.edu/pear-rust'},
            {'title': 'Pear Rust Identification & Biology — Royal Horticultural Society', 'source': 'RHS Gardening', 'url': 'https://www.rhs.org.uk/disease/pear-rust'},
            {'title': 'Pear (Pyrus spp.) Trellis Rust — Pacific Northwest Plant Disease Management', 'source': 'PNW Handbooks', 'url': 'https://pnwhandbooks.org/plantdisease/host-disease/pear-pyrus-spp-trellis-rust-european-pear-rust'}
        ]
        result['expert_assistance'] = 'Consult a local agricultural extension tree fruit specialist or diagnostic clinic for registered orchard spray schedules.'
        result['treatment_withheld'] = True
        result['withheld_reason'] = 'Chemical treatment withheld: Definitive chemical fungicides require in-person orchard verification.'
        result['treatment_options'] = {
            'cultural': [
                'Alternate host management: inspect and prune out rust galls from nearby juniper bushes.',
                'Autumn cleanup: rake and destroy fallen pear leaves to maintain orchard sanitation.'
            ],
            'biological': [
                'Ensure balanced tree vigor with adequate root moisture and organic compost.'
            ],
            'chemical': [], # STRICTLY EMPTY
            'warnings': [
                'CHEMICAL SAFEGUARD: Definitive chemical fungicides are withheld pending in-person orchard verification.',
                'Never apply fungicides formulated for field crops (like corn or grains) onto fruit trees.',
                'Consult an extension fruit pathologist for timing of protective fungicides if juniper hosts cannot be removed.'
            ]
        }
    else:
        # Treatment and crop-specific guidance strictly withheld for unreliable or incompatible predictions
        result['has_kb_entry'] = False
        result['crop'] = 'Unverified / Inconclusive Host'
        result['condition'] = 'Unverified Condition'
        result['pathogen_type'] = 'Unverified'
        result['causal_agent'] = 'Unverified (Taxonomy outside supported scope)'
        result['severity'] = 'Unverified'
        result['symptoms'] = 'Foliar symptoms cannot be confirmed on an unverified host species.'
        result['cultural_management'] = [
            'Maintain standard cultural hygiene: keep foliage dry and avoid overhead sprinkler irrigation.',
            'Do NOT apply chemical treatments or fertilizers formulated for other crops.'
        ]
        result['recovery_monitoring'] = [
            'Observe emerging vegetative growth for symptom recurrence.',
            'Consult an agricultural extension lab or certified arborist for physical confirmation.'
        ]
        result['prevention_next_cycle'] = [
            'Accurately identify the plant species before implementing seasonal disease prevention or buying chemicals.'
        ]
        result['references'] = [
            {'title': 'National Plant Diagnostic Network (NPDN)', 'source': 'NPDN Extension Laboratories', 'url': 'https://www.npdn.org/'},
            {'title': 'USDA Animal and Plant Health Inspection Service', 'source': 'USDA-APHIS', 'url': 'https://www.aphis.usda.gov/'}
        ]
        result['expert_assistance'] = 'Consult a certified arborist, plant diagnostic clinic, or local university extension service for physical verification.'
        result['treatment_withheld'] = True
        result['withheld_reason'] = (
            "Chemical advice withheld: Host species incompatibility detected" if not is_compatible 
            else "Chemical advice withheld: Prediction uncertainty exceeded safety threshold"
        )
        result['treatment_options'] = {
            'cultural': [
                'Isolate symptomatic foliage and scout adjacent plants for physical symptoms.',
                'Ensure standard field sanitation and avoid overhead irrigation while diagnosis is unconfirmed.'
            ],
            'biological': [
                'Maintain general cultural hygiene and biological soil health.'
            ],
            'chemical': [],  # STRICTLY EMPTY
            'warnings': [
                'SAFETY SAFEGUARD: Definitive chemical treatments (fungicides, bactericides, miticides) are strictly withheld because the diagnostic prediction is uncertain or incompatible.',
                'Do NOT apply chemical products without in-person confirmation by a certified crop advisor, agricultural extension specialist, or diagnostic laboratory.',
                'Applying wrong chemical treatments risks phytotoxic crop damage, unnecessary input expenses, and environmental contamination.'
            ]
        }
        result['immediate_actions'] = [
            'Diagnosis is uncertain or species incompatible: do NOT apply chemical sprays.',
            'Inspect live plants for clear diagnostic signs (pustules, sporulation, concentric rings) under natural sunlight.',
            'Take a clear, well-focused close-up photograph of a single leaf showing both upper and lower surfaces, or submit physical samples to an agricultural extension lab.'
        ]

    return result

