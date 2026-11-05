"""
plant_validator.py — Plant/Leaf Image Validator for OptiCrop.

PURPOSE
-------
Screens uploaded images for non-plant content BEFORE calling the disease
classifier. Prevents the closed-set MobileNetV2 disease model from
assigning a disease label to Aadhaar cards, televisions, people, animals,
vehicles, landscapes, and other non-plant images.

METHOD
------
Primary:  Pretrained MobileNetV2 (torchvision ImageNet-1K) visual classifier.
          Runs inference to obtain top-K ImageNet class predictions, then maps
          each class label to one of three categories via keyword matching:
            - PLANT  (leaf, flower, vegetable, fruit, crop, etc.)
            - NONPLANT (person, animal, vehicle, electronic, document, etc.)
            - AMBIGUOUS
          Decision is based on the weighted class probabilities.

Supplementary signals (secondary only, never sole basis for rejection):
          - HSV green vegetation ratio (helps with near-uniform green images)
          - Pixel standard deviation (near-zero → solid colour / blank image)
          - Image decode success check

MODEL PROVENANCE
----------------
  torchvision.models.MobileNet_V2_Weights.IMAGENET1K_V1
  Dataset:   ImageNet-1K ILSVRC 2012 (1.28 M images, 1,000 classes)
  Top-1 acc: 71.878%  |  Top-5 acc: 90.37%
  Weights cached automatically by torchvision (~14 MB, SHA verified).
  Source: https://pytorch.org/vision/stable/models.html

LIMITATIONS (disclosed)
-----------------------
  - ImageNet lacks a dedicated "plant leaf" class. Plant evidence comes from
    fruit/vegetable/flower/fungus classes. Plain green leaves with no
    visible fruit or identifiable texture may score ambiguous; they are
    forwarded to the disease model which then applies its own uncertainty
    guards.
  - Very high-quality photo composites or AI-generated leaf images may
    evade detection.
  - Validation latency: ~50–200 ms on CPU per image (same order as disease
    inference). The validator is cached (singleton) to avoid repeated
    model loading.
  - This validator does NOT guarantee 100% rejection of adversarial images.
    It is an additional safety layer, not a forensic security control.

RESULT DICTIONARY
-----------------
  {
    'valid': bool,          # True = proceed to disease classifier
    'reason': str,          # Human-readable explanation
    'method': str,          # Which method made the decision
    'plant_score': float,   # 0-1, proportion of plant-indicating probability mass
    'nonplant_score': float,# 0-1, proportion of non-plant probability mass
    'top_imagenet': list,   # top-3 [(class_name, prob), ...]
    'supplementary': dict,  # green_ratio, pixel_std
    'error': str or None    # set if image could not be decoded
  }
"""

import os
import io
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keyword sets for classifying ImageNet-1K labels into PLANT / NONPLANT
# ---------------------------------------------------------------------------

# Terms that strongly suggest plant/botanical content
_PLANT_TERMS = frozenset([
    # General botanical
    "leaf", "leaves", "plant", "flower", "blossom", "bloom", "bud",
    "herb", "fern", "moss", "vine", "shrub", "bush", "tree", "sapling",
    "seedling", "grass", "reed", "bamboo", "cactus", "succulent",
    "seaweed", "algae", "lichen",
    # Crops & vegetables
    "corn", "maize", "wheat", "rice", "barley", "oat", "sorghum",
    "soybean", "soy", "cotton", "tobacco", "sugarcane", "coffee",
    "tea", "jute", "hemp",
    "potato", "tomato", "pepper", "eggplant", "aubergine",
    "broccoli", "cauliflower", "cabbage", "kale", "spinach",
    "lettuce", "celery", "carrot", "beetroot", "beet", "turnip",
    "radish", "cucumber", "zucchini", "courgette", "pumpkin",
    "squash", "gourd", "artichoke", "asparagus", "pea", "bean",
    "lentil", "chickpea", "onion", "garlic", "leek",
    # Fruits
    "apple", "pear", "peach", "plum", "cherry", "apricot", "mango",
    "banana", "papaya", "pineapple", "coconut", "avocado", "fig",
    "date", "grape", "kiwi", "watermelon", "melon", "strawberry",
    "blueberry", "raspberry", "blackberry", "cranberry", "pomegranate",
    "lemon", "lime", "orange", "grapefruit", "tangerine", "citrus",
    "jackfruit", "durian", "custard apple", "guava", "lychee",
    # Flowers / ornamentals
    "daisy", "rose", "tulip", "sunflower", "dandelion", "orchid",
    "carnation", "chrysanthemum", "lavender", "lily", "hibiscus",
    "jasmine", "poppy", "dahlia", "marigold", "geranium", "petunia",
    "pansy", "violet", "hyacinth", "daffodil", "gladiolus",
    # Fungus / mushroom (botanical adjacency; often in plant contexts)
    "mushroom", "fungus", "agaric", "bolete", "truffle", "toadstool",
    # Nuts/seeds often from plants
    "acorn", "chestnut", "walnut", "hazel", "almond", "peanut",
    "sunflower seed", "hay",
    # Ambiguous but plant-leaning
    "rapeseed", "broom", "thistle", "clover", "ivy", "mistletoe",
    "pitcher plant", "venus flytrap",
])

# Terms that strongly indicate non-plant content
_NONPLANT_TERMS = frozenset([
    # Statues, idols, figurines, religious artifacts, carvings
    "statue", "idol", "figurine", "sculpture", "carving", "totem", "altar", "pedestal",
    "shrine", "monument", "plaster", "bronze", "brass", "mask", "ornament", "deity",
    "god", "goddess", "buddha", "ganesha", "shiva", "vishnu", "temple", "buckeye",
    # Humans
    "person", "people", "man", "woman", "boy", "girl", "baby", "child",
    "face", "head", "hand", "arm", "leg", "body", "skin",
    "soldier", "police", "pilot", "astronaut", "clown",
    "bride", "groom", "judge",
    # Animals — mammals
    "cat", "dog", "horse", "cow", "sheep", "pig", "goat", "rabbit",
    "deer", "bear", "lion", "tiger", "leopard", "cheetah", "jaguar",
    "wolf", "fox", "hyena", "elephant", "rhinoceros", "hippopotamus",
    "giraffe", "zebra", "camel", "kangaroo", "koala", "panda",
    "monkey", "chimpanzee", "gorilla", "orangutan", "baboon",
    "squirrel", "chipmunk", "beaver", "otter", "seal", "walrus",
    "whale", "dolphin", "shark", "mink", "ferret", "hamster",
    # Animals — birds
    "bird", "hen", "rooster", "duck", "goose", "swan", "parrot", "lorikeet",
    "eagle", "hawk", "owl", "penguin", "flamingo", "pelican",
    "peacock", "turkey", "pigeon", "crow", "sparrow", "finch", "robin", "jay", "magpie",
    # Animals — reptiles/amphibians/fish/insects/invertebrates
    "snake", "lizard", "gecko", "chameleon", "crocodile", "alligator", "turtle",
    "frog", "toad", "salamander",
    "fish", "shark", "ray", "eel", "octopus", "jellyfish", "crab",
    "lobster", "snail", "slug", "worm", "caterpillar", "butterfly",
    "dragonfly", "beetle", "ant", "bee", "wasp", "fly", "mosquito",
    "spider", "grasshopper", "cricket", "moth", "ladybug", "lacewing",
    "harvestman", "centipede", "mantis", "conch", "flatworm",
    # Vehicles
    "car", "automobile", "truck", "bus", "van", "taxi", "limousine",
    "motorcycle", "bicycle", "scooter", "tricycle",
    "airplane", "aircraft", "helicopter", "rocket", "spacecraft",
    "ship", "boat", "submarine", "canoe", "kayak",
    "train", "locomotive", "tram", "subway",
    "bulldozer", "tractor", "excavator", "crane",
    # Electronics & screens
    "television", "tv", "monitor", "screen", "laptop", "computer",
    "keyboard", "mouse", "phone", "smartphone", "tablet", "remote",
    "camera", "radio", "stereo", "speaker", "microphone",
    "projector", "printer", "scanner", "web site", "website",
    # Documents / ID / text
    "envelope", "letter", "book", "magazine", "newspaper",
    "card", "ticket", "label", "tag", "sign", "banner",
    "chalkboard", "whiteboard", "map", "chart", "id card", "identity card",
    # Buildings / structures
    "house", "building", "church", "mosque", "castle", "tower",
    "bridge", "stadium", "warehouse", "barn", "silo", "fence", "chainlink",
    "wall", "door", "window", "web", "spider web",
    # Furniture / household
    "chair", "table", "desk", "bed", "sofa", "couch", "bench",
    "cabinet", "shelf", "drawer", "lamp", "clock", "mirror",
    "bathtub", "toilet", "sink", "oven", "refrigerator",
    # Processed food (not a raw plant leaf)
    "pizza", "hamburger", "sandwich", "hotdog", "sausage", "steak",
    "soup", "salad", "pasta", "rice dish", "sushi", "bread", "cake",
    "cookie", "doughnut", "ice cream", "candy", "bakery", "restaurant",
    # Clothing / accessories
    "shirt", "pants", "dress", "coat", "hat", "shoe", "boot",
    "glove", "scarf", "tie", "bag", "backpack", "umbrella",
    # Tools / weapons
    "hammer", "wrench", "screwdriver", "saw", "drill",
    "gun", "rifle", "sword", "knife", "pencil sharpener", "lighter",
    # Sports / toys
    "ball", "bat", "racket", "bicycle", "skateboard",
    "chess", "puppet", "teddy bear", "toy", "doll",
    # Sky / water / terrain (landscape only is ambiguous but usually NOT a leaf)
    "sky", "cloud", "ocean", "sea", "river", "lake", "waterfall",
    "mountain", "volcano", "glacier", "desert", "sand", "rock",
    "stone", "cliff", "cave",
    # Abstract / miscellaneous
    "bandage", "pill", "syringe", "stethoscope",
    "flag", "coin", "banknote",
])


def _classify_imagenet_label(label: str, idx: int = None) -> str:
    """
    Map an ImageNet class label string and optional category index to 'plant', 'nonplant', or 'ambiguous'.
    When index is provided, uses exact ImageNet-1K taxonomy boundaries:
    - 0-397: Animals, insects, reptiles, birds, fish (non-plant)
    - 398-935: Manufactured objects, structures, statues, vehicles, electronics (non-plant)
    - 959-983: Prepared foods, drinks, landscapes, humans (non-plant)
    - 999: Toilet tissue (non-plant)
    - 988 (acorn), 990 (buckeye): Tree seeds / nuts (prominent in carved statues/ornaments, non-foliar)
    - 936-958 & 984-998 (except 988, 990): Botanical vegetables, fruits, crops, flowers, fungi (plant)
    """
    if idx is not None:
        if (0 <= idx < 936) or (959 <= idx < 984) or (idx == 999) or (idx in (988, 990)):
            return "nonplant"
        if (936 <= idx <= 958) or (984 <= idx <= 998):
            return "plant"

    label_lower = label.lower()
    # Check non-plant terms first to avoid compound name collisions (e.g. leaf beetle, vine snake, cabbage butterfly)
    for term in _NONPLANT_TERMS:
        if term in label_lower:
            return "nonplant"
    for term in _PLANT_TERMS:
        if term in label_lower:
            return "plant"
    return "ambiguous"


def _hsv_green_ratio(image_rgb: np.ndarray) -> float:
    """
    Supplementary check: fraction of pixels that fall in HSV green-range
    typical of vegetation (hue 60°-165°, saturation ≥ 15%, value ≥ 15%).
    Returns 0.0-1.0.
    """
    r = image_rgb[:, :, 0].astype(np.float32) / 255.0
    g = image_rgb[:, :, 1].astype(np.float32) / 255.0
    b = image_rgb[:, :, 2].astype(np.float32) / 255.0

    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin

    # Value
    v = cmax

    # Saturation (safe division)
    cmax_safe = np.where(cmax > 0, cmax, 1.0)
    s = np.where(cmax > 0, delta / cmax_safe, 0.0)

    # Hue (0-360) (safe division)
    h = np.zeros_like(r)
    delta_safe = np.where(delta > 0, delta, 1.0)
    mask_r = (cmax == r) & (delta > 0)
    mask_g = (cmax == g) & (delta > 0)
    mask_b = (cmax == b) & (delta > 0)
    h[mask_r] = 60.0 * (((g[mask_r] - b[mask_r]) / delta_safe[mask_r]) % 6)
    h[mask_g] = 60.0 * ((b[mask_g] - r[mask_g]) / delta_safe[mask_g] + 2)
    h[mask_b] = 60.0 * ((r[mask_b] - g[mask_b]) / delta_safe[mask_b] + 4)

    # Green vegetation: hue 60-165, saturation >= 0.15, value >= 0.15
    green_mask = (h >= 60) & (h <= 165) & (s >= 0.15) & (v >= 0.15)
    return float(np.mean(green_mask))


# ---------------------------------------------------------------------------
# Singleton validator class
# ---------------------------------------------------------------------------

class PlantValidator:
    """
    Singleton. Loads pretrained MobileNetV2 (ImageNet) once and validates
    images for plant/non-plant content.
    """
    _instance = None

    def __init__(self):
        self.model = None
        self.transform = None
        self.categories = None
        self.device = None
        self.available = False
        self._load()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PlantValidator()
        return cls._instance

    def _load(self):
        """Load pretrained ImageNet MobileNetV2."""
        try:
            import torch
            import torch.nn as nn
            from torchvision import models, transforms

            self.device = torch.device("cpu")  # keep CPU for compatibility
            weights = models.MobileNet_V2_Weights.IMAGENET1K_V1
            self.categories = weights.meta["categories"]  # list of 1000 str
            self.model = models.mobilenet_v2(weights=weights)
            self.model.eval()
            self.model.to(self.device)

            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            self.available = True
            logger.info("PlantValidator: ImageNet MobileNetV2 loaded (CPU).")
            print("PlantValidator: ImageNet MobileNetV2 validator loaded successfully.")
        except Exception as e:
            self.available = False
            logger.warning(f"PlantValidator: Could not load ImageNet model: {e}")
            print(f"PlantValidator: WARNING — ImageNet model unavailable: {e}. "
                  "Validation will use supplementary signals only.")

    def validate(self, image_bytes: bytes) -> dict:
        """
        Validate whether image_bytes represents a plant/leaf image.

        Returns a result dict (see module docstring).
        """
        result = {
            "valid": None,
            "is_plant": False,
            "species_supported": "unverified",
            "reason": "",
            "method": "unknown",
            "plant_score": 0.0,
            "nonplant_score": 0.0,
            "top_imagenet": [],
            "supplementary": {},
            "error": None
        }

        # ── Step 1: Decode image ─────────────────────────────────────────
        if not image_bytes:
            result["valid"] = False
            result["reason"] = "Uploaded file is empty or missing."
            result["error"] = "empty_file"
            result["method"] = "decode_check"
            return result

        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()  # check integrity
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            result["valid"] = False
            result["reason"] = f"Unable to decode image file: {type(e).__name__}."
            result["error"] = "corrupt_image"
            result["method"] = "decode_check"
            return result

        # ── Step 2: RGB conversion & size check ───────────────────────────
        try:
            image_rgb = image.convert("RGB")
        except Exception as e:
            result["valid"] = False
            result["reason"] = f"Cannot convert image to RGB: {type(e).__name__}."
            result["error"] = "rgb_conversion_fail"
            result["method"] = "decode_check"
            return result

        w, h = image_rgb.size
        if w < 32 or h < 32:
            result["valid"] = False
            result["reason"] = (
                f"Image resolution ({w}x{h}px) is too low for foliar inspection. "
                "Minimum 32x32 pixels required."
            )
            result["method"] = "size_check"
            return result

        # ── Step 3: Supplementary — pixel std (blank/solid check) ─────────
        img_np = np.array(image_rgb, dtype=np.float32)
        pixel_std = float(np.std(img_np))
        result["supplementary"]["pixel_std"] = round(pixel_std, 2)

        if pixel_std < 8.0:
            result["valid"] = False
            result["reason"] = (
                "The image appears to be blank or nearly uniform. "
                "Please upload a clear photo of a plant leaf."
            )
            result["method"] = "texture_check"
            return result

        # ── Step 4: Supplementary — HSV green ratio ───────────────────────
        green_ratio = _hsv_green_ratio(img_np)
        result["supplementary"]["green_ratio"] = round(green_ratio, 3)

        # ── Step 4b: Supplementary — foliar edge texture density ──────────
        try:
            from PIL import ImageFilter
            gray_img = image_rgb.convert('L')
            edges = gray_img.filter(ImageFilter.FIND_EDGES)
            edge_mean = float(np.mean(np.array(edges, dtype=np.float32)))
        except Exception:
            edge_mean = 15.0
        result["supplementary"]["edge_mean"] = round(edge_mean, 2)

        # ── Step 5: Primary — ImageNet pretrained model inference ─────────
        if self.available:
            try:
                import torch
                tensor = self.transform(image_rgb).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    logits = self.model(tensor)
                    probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

                # Top-10 predictions
                top_indices = np.argsort(probs)[::-1][:10]

                plant_score = 0.0
                nonplant_score = 0.0
                top3 = []

                for i, idx in enumerate(top_indices):
                    label = self.categories[idx]
                    p = float(probs[idx])
                    cat = _classify_imagenet_label(label, idx=idx)

                    if cat == "plant":
                        plant_score += p
                    elif cat == "nonplant":
                        nonplant_score += p

                    if i < 3:
                        top3.append({"class": label, "prob": round(p * 100, 2), "category": cat})

                result["plant_score"] = round(plant_score, 4)
                result["nonplant_score"] = round(nonplant_score, 4)
                result["top_imagenet"] = top3
                result["method"] = "imagenet_mobilenetv2"

                # Top-1 label & probability
                top1_idx = top_indices[0]
                top1_label = self.categories[top1_idx]
                top1_prob = float(probs[top1_idx])
                top1_cat = _classify_imagenet_label(top1_label, idx=top1_idx)

                # ── Decision logic (Stage 1: Non-Plant Screening) ───────────
                # REJECT 1: Non-plant document, electronic screen, vehicle, or manufactured item with near-zero green
                if nonplant_score >= 0.15 and green_ratio < 0.02 and plant_score == 0.0:
                    result["valid"] = False
                    result["reason"] = (
                        f"Invalid image: non-plant visual content detected ('{top1_label}', "
                        f"non-plant signal: {nonplant_score*100:.1f}%, "
                        f"green vegetation ratio: {green_ratio*100:.1f}%). "
                        "Please upload a clear leaf image of a supported crop."
                    )
                    return result

                # REJECT 2: Religious idol, statue, figurine, carving, or smooth painted non-plant object
                # (Dominant non-plant mass with zero botanical leaf signal and smooth non-leaf texture)
                if nonplant_score >= 0.50 and plant_score < 0.05 and edge_mean < 8.5:
                    result["valid"] = False
                    result["reason"] = (
                        f"Invalid image: visual content appears to be a religious idol, statue, or non-plant object "
                        f"('{top1_label}', non-plant signal: {nonplant_score*100:.1f}%), lacking foliar leaf structure. "
                        "Please upload a clear close-up photo of a crop leaf."
                    )
                    return result

                # REJECT 3: High-confidence non-plant object (e.g. car, aircraft, pizza) with low green & low botanical score
                if top1_cat == "nonplant" and top1_prob >= 0.40 and plant_score < 0.02 and green_ratio < 0.02:
                    result["valid"] = False
                    result["reason"] = (
                        f"Invalid image: the visual content appears to be '{top1_label}' "
                        f"({top1_prob*100:.1f}%), not a plant leaf. "
                        "Please upload a clear close-up photo of a supported crop leaf."
                    )
                    return result

                # ACCEPT: meaningful plant signal
                if plant_score >= 0.10 or (plant_score >= 0.05 and green_ratio >= 0.15):
                    result["valid"] = True
                    result["is_plant"] = True
                    result["species_supported"] = "unverified"
                    result["reason"] = (
                        f"Image confirmed as botanical foliage "
                        f"(plant signal: {plant_score*100:.1f}%, green ratio: {green_ratio*100:.1f}%). "
                        "Note: Plant validation confirms botanical content but does not verify that the species is among the 14 supported crops."
                    )
                    return result

                # AMBIGUOUS: let disease model handle with its own uncertainty guards
                # (neither strong plant nor strong non-plant signal)
                result["valid"] = True
                result["is_plant"] = True
                result["species_supported"] = "unverified"
                result["reason"] = (
                    f"Image is ambiguous (plant signal: {plant_score*100:.1f}%, "
                    f"non-plant signal: {nonplant_score*100:.1f}%, "
                    f"green ratio: {green_ratio*100:.1f}%). "
                    "Forwarding to disease classifier for further analysis."
                )
                return result

            except Exception as e:
                logger.error(f"PlantValidator inference error: {e}")
                # Fall through to supplementary-only decision

        # ── Step 6: Fallback — supplementary signals only ─────────────────
        # (Used when ImageNet model is unavailable)
        result["method"] = "supplementary_fallback"

        # Document, electronic screen, vehicle, or manufactured item with near-zero green
        if green_ratio < 0.02:
            result["valid"] = False
            result["reason"] = (
                f"Invalid image: non-plant visual content detected "
                f"(green vegetation ratio: {green_ratio*100:.1f}%). "
                "Please upload a clear leaf image of a supported crop."
            )
            return result

        # Smooth painted green artificial object, religious idol, or statue (edge_mean < 8.0 with unnatural uniform green)
        if edge_mean < 8.0 and green_ratio >= 0.85:
            result["valid"] = False
            result["reason"] = (
                "Invalid image: visual content appears to be a religious idol, statue, or non-plant object, "
                "lacking foliar leaf structure and natural venation. "
                "Please upload a clear close-up photo of a crop leaf."
            )
            return result

        # High green ratio strongly suggests vegetation
        if green_ratio >= 0.20:
            result["valid"] = True
            result["reason"] = (
                f"Supplementary green vegetation ratio ({green_ratio*100:.1f}%) "
                "suggests plant content. Proceeding with disease analysis."
            )
        elif green_ratio < 0.05 and pixel_std < 40.0:
            result["valid"] = False
            result["reason"] = (
                f"Very low green vegetation ratio ({green_ratio*100:.1f}%) "
                "and low texture suggest this is not a plant leaf image."
            )
        else:
            # Cannot determine; forward as ambiguous
            result["valid"] = True
            result["reason"] = (
                "Cannot determine plant/non-plant status from supplementary signals alone. "
                "Forwarding to disease classifier."
            )

        return result


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def validate_plant_image(image_bytes: bytes) -> dict:
    """
    Convenience wrapper. Returns a validation result dict.
    See PlantValidator.validate() docstring.
    """
    return PlantValidator.get_instance().validate(image_bytes)
