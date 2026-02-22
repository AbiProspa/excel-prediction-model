import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os
import sys

# Define path to history.csv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.csv")

def evaluate_predictions(actual_values, predicted_values):
    """
    Evaluates the Bayesian model's predictive accuracy using MAE and MSE.
    
    Args:
        actual_values (list or pd.Series): The ground truth/actual outcomes (e.g., 0.0 to 1.0).
        predicted_values (list or pd.Series): The model's predicted probability scores.
        
    Returns:
        dict: A dictionary containing the MAE and MSE scores.
    """
    if len(actual_values) == 0:
        print("No data available for evaluation.")
        return {"MAE": None, "MSE": None}

    # Calculate metrics using scikit-learn
    mae = mean_absolute_error(actual_values, predicted_values)
    mse = mean_squared_error(actual_values, predicted_values)
    
    # Display the results
    print("\n--- MODEL EVALUATION RESULTS ---")
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"Mean Squared Error (MSE):  {mse:.4f}")
    print("--------------------------------\n")
    
    return {"MAE": mae, "MSE": mse}

def load_and_evaluate(file_path=HISTORY_FILE):
    """
    Loads history data and runs evaluation.
    Only considers rows where 'outcome' is a valid number (0.0 - 1.0).
    """
    print(f"Loading history from: {file_path}")
    
    if not os.path.exists(file_path):
        print("❌ History file not found.")
        return

    try:
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        if 'outcome' not in df.columns or 'final_prob' not in df.columns:
            print("❌ Missing 'outcome' or 'final_prob' columns in history file.")
            return

        # Filter for valid numerical outcomes (ignore 'Pending' or empty)
        valid_df = df[pd.to_numeric(df['outcome'], errors='coerce').notnull()].copy()
        
        if valid_df.empty:
            print("⚠️ No valid outcomes found (all are 'Pending' or invalid). Cannot evaluate yet.")
            print("To test, manually update some 'Pending' outcomes in history.csv to 0.0 (Safe) or 1.0 (Risk).")
            return

        # Ensure no NaNs in prediction column
        valid_df = valid_df[pd.to_numeric(valid_df['final_prob'], errors='coerce').notnull()]

        if valid_df.empty:
             print("⚠️ No records with both valid outcome and valid probability score found.")
             return

        y_true = valid_df['outcome'].astype(float)
        y_pred = valid_df['final_prob'].astype(float)
        
        print(f"Evaluating on {len(valid_df)} records...")
        return evaluate_predictions(y_true, y_pred)

    except Exception as e:
        print(f"❌ Error loading or evaluating data: {e}")

# --- Example Usage / Test ---
if __name__ == "__main__":
    # check for command line arg to run on history
    if len(sys.argv) > 1 and sys.argv[1] == '--history':
        load_and_evaluate()
    else:
        print("Running with dummy data for verification...")
        # Dummy data: representing 5 feedback instances
        # Actual could be a known historical risk outcome (0.0 = Safe, 1.0 = Critical Issue)
        y_true = [0.0, 1.0, 0.0, 0.5, 1.0] 
        
        # Predicted probabilities from your Bayesian model
        y_pred = [0.1, 0.9, 0.2, 0.6, 0.8] 
        
        evaluate_predictions(y_true, y_pred)
        print("\nTo run on actual history file, use: python evaluate_model.py --history")
