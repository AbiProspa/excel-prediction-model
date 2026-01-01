import json
import os

# Use absolute path relative to this file to avoid CWD issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHT_FILE = os.path.join(BASE_DIR, "weights.json")

def load_weights():
    if not os.path.exists(WEIGHT_FILE):
        return {"rating_weight": 0.5, "sentiment_weight": 0.5}
    try:
        with open(WEIGHT_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load weights ({e}). Using defaults.")
        return {"rating_weight": 0.5, "sentiment_weight": 0.5}

def save_weights(weights):
    # Normalize
    total = weights["rating_weight"] + weights["sentiment_weight"]
    if total > 0:
        weights["rating_weight"] /= total
        weights["sentiment_weight"] /= total
    
    try:
        with open(WEIGHT_FILE, "w") as f:
            json.dump(weights, f, indent=2)
    except Exception as e:
        print(f"Error saving weights: {e}")
