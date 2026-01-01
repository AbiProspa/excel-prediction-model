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
from feedback_loop import log_result

# ========================================
# CENTRALIZED EXCEL CONFIGURATION
# ========================================
EXCEL_FILE_PATH = r"C:\Users\abiod\Documents\GitHub\scratch\prediction_model\data\Feedback_Dashboard_Template.xlsm"
INPUT_SHEET = "Feedback_Data"
OUTPUT_SHEET = "Output"


def run_model(excel_path=EXCEL_FILE_PATH):
    """
    Main model pipeline that reads from Feedback_Data and writes to Output.
    """
    print("="*60)
    print("HYBRID ADAPTIVE AI MODEL (BERT + BAYESIAN + LEARNING)")
    print("="*60)
    print(f"Excel File: {excel_path}")
    
    try:
        # 1. Load Data
        print("\n[1/7] Loading data...")
        df = load_feedback_data(excel_path, INPUT_SHEET)
        
        if df.empty:
            print("❌ No data loaded. Exiting.")
            return
        
        print(f"✓ Loaded {len(df)} records")

        # 2. NLP Analysis (DistilBERT)
        print("\n[2/7] Running NLP Analysis (BERT)...")
        df_nlp = analyze_comments(df)
        print(f"✓ Sentiment analysis complete")
        
        # 3. Bayesian Probability Model (Adaptive Weights)
        print("\n[3/7] Calculating Probabilities (Adaptive)...")
        prob_df = calculate_probabilities(df_nlp)
        print(f"✓ Probability scores computed for {len(prob_df)} feedback types")
        
        # 4. Risk Scoring
        print("\n[4/7] Assessing Risk...")
        risk_df = assess_risk(prob_df)
        print(f"✓ Risk levels assigned")
        
        # 5. Recommendation Engine
        print("\n[5/7] Generating Recommendations...")
        final_df = generate_recommendations(risk_df)
        print(f"✓ Recommendations generated")
        
        # 6. History Logging (Learning Loop)
        print("\n[6/7] Logging to History (Feedback Loop)...")
        for _, row in final_df.iterrows():
            log_data = {
                "feedback_type": row.get('Feedback Type'),
                "rating": row.get('Average Rating'),
                "sentiment_prob": row.get('Average Sentiment Score'), # This is the neg prob now
                "final_prob": row.get('Probability Score'),
                "risk": row.get('Risk Level'),
                "action": row.get('Recommendation'),
                "outcome": "Pending" # Placeholder for future outcome
            }
            log_result(log_data)
        print(f"✓ {len(final_df)} records logged to history.csv")
        
        # 7. Export Results
        print("\n[7/7] Exporting Results...")
        export_to_excel(final_df, excel_path, OUTPUT_SHEET)
        
        print("\n" + "="*60)
        print("✅ MODEL RUN COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


@xw.sub
def run_model_from_excel():
    """
    Excel-callable function.
    """
    print("\n🔵 Model triggered from Excel")
    wb = xw.Book.caller()
    run_model(wb.fullname)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Adaptive Hybrid AI Model')
    parser.add_argument(
        '--excel-path', 
        default=EXCEL_FILE_PATH,
        help='Path to Excel file'
    )
    
    args = parser.parse_args()
    run_model(args.excel_path)

