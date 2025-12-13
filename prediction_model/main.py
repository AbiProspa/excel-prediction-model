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

# ========================================
# CENTRALIZED EXCEL CONFIGURATION
# ========================================
EXCEL_FILE_PATH = r"C:\Users\abiod\Documents\GitHub\scratch\prediction_model\data\Feedback_Dashboard_Template.xlsx"
INPUT_SHEET = "Feedback_Data"
OUTPUT_SHEET = "Output"


def run_model(excel_path=EXCEL_FILE_PATH):
    """
    Main model pipeline that reads from Feedback_Data and writes to Output.
    
    Args:
        excel_path (str): Path to the Excel file containing input and output sheets.
    """
    print("="*60)
    print("PREDICTION & RECOMMENDATION MODEL")
    print("="*60)
    print(f"Excel File: {excel_path}")
    print(f"Input Sheet: {INPUT_SHEET}")
    print(f"Output Sheet: {OUTPUT_SHEET}")
    print("="*60)
    
    try:
        # 1. Load Data from Feedback_Data sheet
        print("\n[1/6] Loading data...")
        df = load_feedback_data(excel_path, INPUT_SHEET)
        
        if df.empty:
            print("❌ No data loaded. Exiting.")
            return
        
        print(f"✓ Loaded {len(df)} records")

        # 2. NLP Analysis
        print("\n[2/6] Running NLP Analysis...")
        df_nlp = analyze_comments(df)
        print(f"✓ Sentiment analysis complete")
        
        # 3. Bayesian Probability Model
        print("\n[3/6] Calculating Probabilities...")
        prob_df = calculate_probabilities(df_nlp)
        print(f"✓ Probability scores computed for {len(prob_df)} feedback types")
        
        # 4. Risk Scoring
        print("\n[4/6] Assessing Risk...")
        risk_df = assess_risk(prob_df)
        print(f"✓ Risk levels assigned")
        
        # 5. Recommendation Engine
        print("\n[5/6] Generating Recommendations...")
        final_df = generate_recommendations(risk_df)
        print(f"✓ Recommendations generated")
        
        # 6. Export Results to Output sheet
        print("\n[6/6] Exporting Results...")
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
    Excel-callable function using xlwings @xw.sub decorator.
    This can be triggered directly from an Excel macro/button.
    """
    print("\n🔵 Model triggered from Excel")
    run_model(EXCEL_FILE_PATH)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Excel-Connected Prediction & Recommendation Model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Default Configuration:
  Excel File: {EXCEL_FILE_PATH}
  Input Sheet: {INPUT_SHEET}
  Output Sheet: {OUTPUT_SHEET}
        """
    )
    parser.add_argument(
        '--excel-path', 
        default=EXCEL_FILE_PATH,
        help='Path to Excel file (default: configured path)'
    )
    
    args = parser.parse_args()
    
    # Run the model
    run_model(args.excel_path)

