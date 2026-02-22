import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Define constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.csv")

def generate_rich_history(num_records=50):
    print(f"Generating {num_records} resolved records for history...")
    
    categories = ["ATM", "App", "Loan Process", "Online Banking", "Service"]
    actions = {
        "Critical": "Immediate investigation required. High risk detected.",
        "Warning": "Monitor closely. Follow-up recommended.",
        "Stable": "Standard monitoring. No immediate action."
    }
    
    data = []
    now = datetime.now()
    
    # NLP Keywords for context
    safe_keywords = ["smooth", "fast", "thanks", "helpful"]
    risk_keywords = ["failed", "crash", "broken", "fraud", "error", "timeout", "terrible"]
    
    for i in range(num_records):
        # Decide if this is a "Risk" or "Safe" record (Balanced mix)
        is_risk = np.random.choice([0.0, 1.0], p=[0.6, 0.4])
        
        category = np.random.choice(categories)
        date = (now - timedelta(days=np.random.randint(1, 30))).isoformat()
        
        if is_risk == 1.0:
            rating = np.random.uniform(1.0, 2.5)
            sentiment_prob = np.random.uniform(0.7, 1.0)
            risk_level = "Critical"
            outcome = 1.0
        else:
            rating = np.random.uniform(4.0, 5.0)
            sentiment_prob = np.random.uniform(0.0, 0.3)
            risk_level = "Stable"
            outcome = 0.0
            
        # Add some noise/variance
        final_prob = (0.5 * ( (5-rating)/4 ) + 0.5 * sentiment_prob)
        
        data.append({
            "date": date,
            "feedback_type": category,
            "rating": round(rating, 2),
            "sentiment_prob": round(sentiment_prob, 4),
            "final_prob": round(final_prob, 4),
            "risk": risk_level,
            "action": actions[risk_level],
            "outcome": outcome
        })

    df = pd.DataFrame(data)
    
    # Save to history.csv (Overwrite for clean baseline)
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    df.to_csv(HISTORY_FILE, index=False)
    print(f"Successfully wrote {num_records} records to {HISTORY_FILE}")

if __name__ == "__main__":
    generate_rich_history()
