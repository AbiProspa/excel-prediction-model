import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# prediction_model/data/history.csv
HISTORY_FILE = os.path.join(BASE_DIR, "prediction_model", "data", "history.csv")

def update_history():
    if not os.path.exists(HISTORY_FILE):
        print(f"File not found: {HISTORY_FILE}")
        return

    print(f"Reading {HISTORY_FILE}...")
    try:
        df = pd.read_csv(HISTORY_FILE)
        
        if df.empty:
            print("History file is empty.")
            return

        print(f"Total records: {len(df)}")
        
        # Update last 5 records
        # Set outcome based on final_prob (just for demo purposes)
        # If prob > 0.5, outcome = 1.0 (Risk), else 0.0 (Safe)
        
        updates_made = 0
        for i in range(max(0, len(df) - 5), len(df)):
            current_outcome = str(df.at[i, 'outcome'])
            if current_outcome.lower() in ['pending', 'nan', '']:
                prob = float(df.at[i, 'final_prob']) if pd.notnull(df.at[i, 'final_prob']) else 0.0
                new_outcome = 1.0 if prob > 0.5 else 0.0
                df.at[i, 'outcome'] = new_outcome
                print(f"Row {i}: Changed '{current_outcome}' -> {new_outcome} (Prob: {prob})")
                updates_made += 1
        
        if updates_made > 0:
            df.to_csv(HISTORY_FILE, index=False)
            print(f"Successfully updated {updates_made} records.")
        else:
            print("No 'Pending' records found in the last 5 rows to update.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_history()
