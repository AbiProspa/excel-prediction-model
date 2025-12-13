import os
import sys
import xlwings as xw
import pandas as pd

# Add the src directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from load_data import load_feedback_data
from nlp_engine import analyze_comments
from bayesian_model import calculate_probabilities
from risk_engine import assess_risk
from recommendation_engine import generate_recommendations
from export_results import export_to_excel

def main(input_path=None, output_path=None, sheet_name='ModelOutput'):
    print("Starting Prediction Model...")
    
    # Define file path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if input_path:
        data_path = input_path
    else:
        data_path = os.path.join(base_dir, 'data', 'feedback.xlsx')
        
    if output_path:
        target_path = output_path
    else:
        target_path = data_path # Default to same file if not specified

    print(f"Input Data: {data_path}")
    print(f"Output Target: {target_path} (Sheet: {sheet_name})")
    
    # 1. Load Data
    print("Loading data...")
    df = load_feedback_data(data_path)
    if df.empty:
        print("No data loaded. Exiting.")
        return

    # 2. NLP Analysis
    print("Running NLP Analysis...")
    df_nlp = analyze_comments(df)
    
    # 3. Bayesian Probability Model
    print("Calculating Probabilities...")
    prob_df = calculate_probabilities(df_nlp)
    
    # 4. Risk Scoring
    print("Assessing Risk...")
    risk_df = assess_risk(prob_df)
    
    # 5. Recommendation Engine
    print("Generating Recommendations...")
    final_df = generate_recommendations(risk_df)
    
    # 6. Export Results
    print("Exporting Results...")
    export_to_excel(final_df, target_path, sheet_name)
    
    print("Model run complete.")

@xw.func
def run_model():
    main()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Prediction Model')
    parser.add_argument('--input', help='Path to input Excel file')
    parser.add_argument('--output', help='Path to output Excel file')
    parser.add_argument('--sheet', default='ModelOutput', help='Name of the output sheet')
    
    args = parser.parse_args()
    
    main(args.input, args.output, args.sheet)
