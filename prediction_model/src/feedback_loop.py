import csv
import os
from datetime import datetime
from learning_engine import load_weights, save_weights

# Store history in data directory (sibling to src)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.csv")

def ensure_history_file():
    if not os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "w", newline="", encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["date", "feedback_type", "rating", "sentiment_prob", "final_prob", "risk", "action", "outcome"])
        except Exception as e:
            print(f"Error creating history file: {e}")

def log_result(data):
    ensure_history_file()
    try:
        with open(HISTORY_FILE, "a", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                data.get("feedback_type", ""),
                data.get("rating", ""),
                data.get("sentiment_prob", ""),
                data.get("final_prob", ""),
                data.get("risk", ""),
                data.get("action", ""),
                data.get("outcome", "")
            ])
    except Exception as e:
        print(f"Error logging result: {e}")

def update_weights(prediction_correct: bool):
    """
    Updates the weights based on whether the model's prediction was correct.
    If prediction was correct (meaning High Probability matched High Risk issue), we trust the dominant signal.
    Actually, the logic in the blueprint was:
    if prediction_was_correct:
        w_sentiment += 0.05
    else:
        w_rating += 0.05
    
    This is a simplification. 
    If the model predicted HIGH RISK and it WAS a high risk, we reinforce the current weights?
    Or if the model said "High Risk" due to Sentiment, but user says "Correct", we trust Sentiment more?
    
    Blueprint says:
    if prediction_correct:
        weights["sentiment_weight"] += 0.03
    else:
        weights["rating_weight"] += 0.03
    
    We will follow the blueprint exactly.
    """
    weights = load_weights()

    if prediction_correct:
        weights["sentiment_weight"] += 0.03
    else:
        # If prediction was wrong, maybe we rely more on the explicit Rating?
        weights["rating_weight"] += 0.03

    save_weights(weights)
    print(f"Weights updated: {weights}")
