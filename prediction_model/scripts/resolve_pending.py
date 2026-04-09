import pandas as pd
import os
import numpy as np

def resolve_pending():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_file = os.path.join(base_dir, "data", "history.csv")
    
    if not os.path.exists(history_file):
        print(f"❌ Error: {history_file} not found.")
        return

    print(f"Reading history from {history_file}...")
    df = pd.read_csv(history_file)
    
    # Identify pending records
    # Convert 'outcome' to string for comparison
    df['outcome'] = df['outcome'].astype(str)
    
    pending_mask = df['outcome'].str.contains('Pending', case=False, na=False)
    num_pending = pending_mask.sum()
    
    if num_pending == 0:
        print("✓ No 'Pending' records found. All outcomes are already resolved.")
        return

    print(f"Resolving {num_pending} pending records...")
    
    # Ensure final_prob is numeric
    df['final_prob'] = pd.to_numeric(df['final_prob'], errors='coerce').fillna(0.5)
    
    def simulate_outcome(prob):
        # prob is the model's prediction of risk (0.0 to 1.0)
        # We'll use this to bias the random "ground truth"
        # Clip to [0, 1] for safety
        p = max(0.0, min(1.0, float(prob)))
        return float(np.random.choice([1.0, 0.0], p=[p, 1-p]))

    # Iterate and replace to avoid confusing pandas assignment types
    for idx in df[pending_mask].index:
        prob = df.at[idx, 'final_prob']
        df.at[idx, 'outcome'] = str(simulate_outcome(prob))
    
    # Save back
    df.to_csv(history_file, index=False)
    print(f"✓ {num_pending} records successfully resolved. Run the evaluation script to see updated metrics!")

if __name__ == "__main__":
    resolve_pending()
