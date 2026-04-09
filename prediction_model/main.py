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
from evaluate_model import load_and_evaluate

# ========================================
# CENTRALIZED EXCEL CONFIGURATION
# ========================================
# Use relative path for portability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE_PATH = os.path.join(BASE_DIR, "data", "Feedback_Dashboard_Template.xlsm")
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
            print("[ERROR] No data loaded. Exiting.")
            return
        
        print(f"[SUCCESS] Loaded {len(df)} records")

        # 2. NLP Analysis (DistilBERT)
        print("\n[2/7] Running NLP Analysis (BERT)...")
        df_nlp = analyze_comments(df)
        print(f"[SUCCESS] Sentiment analysis complete")
        
        # 3. Bayesian Probability Model (Adaptive Weights)
        print("\n[3/7] Calculating Probabilities (Adaptive)...")
        prob_df = calculate_probabilities(df_nlp)
        print(f"[SUCCESS] Probability scores computed for {len(prob_df)} feedback types")
        
        # 4. Risk Scoring
        print("\n[4/7] Assessing Risk...")
        risk_df = assess_risk(prob_df)
        print(f"[SUCCESS] Risk levels assigned")
        
        # 5. Recommendation Engine
        print("\n[5/7] Generating Recommendations...")
        final_df = generate_recommendations(risk_df)
        print(f"[SUCCESS] Recommendations generated")
        
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
        print(f"[SUCCESS] {len(final_df)} records logged to history.csv")
        
        # 7. Export Results
        print("\n[7/7] Exporting Results...")
        export_to_excel(final_df, excel_path, OUTPUT_SHEET)
        
        # 8. Update Dashboard Summary (User Requested Spot)
        print("\n[8/8] Updating Dashboard Summary...")
        try:
            wb = xw.apps.active.books.active
            dashboard = wb.sheets['Dashboard']
            
            # Map products to their Dashboard rows
            # Risk/Issue Range (H18-I22)
            # Recommendation Panel (L18, L22, L26, L30, L34)
            layout_map = {
                "ATM": {"summary_row": 18, "rec_row": 18},
                "App": {"summary_row": 19, "rec_row": 22},
                "Loan Process": {"summary_row": 20, "rec_row": 26},
                "Online Banking": {"summary_row": 21, "rec_row": 30},
                "Service": {"summary_row": 22, "rec_row": 34}
            }
            
            for product, layout in layout_map.items():
                # Filter results for this product (products are stored in Feedback Type now)
                prod_data = final_df[final_df['Feedback Type'] == product]
                if not prod_data.empty:
                    row = prod_data.iloc[0]
                    risk = row['Risk Level']
                    top_issue = row.get('Top Issue Summary', 'General feedback')
                    rec = row.get('Recommendation', 'Monitor situation.')
                    
                    # 1. Update Risk Level (Column I) - The red box area
                    dashboard.range(f"I{layout['summary_row']}").value = f"{product}  {risk}"
                    
                    # 2. Update Top Issue Summary (Column H)
                    dashboard.range(f"H{layout['summary_row']}").value = top_issue
                    
                    # 3. Update Detailed Recommendation (Column L)
                    dashboard.range(f"L{layout['rec_row']}").value = rec
                    
            print(f"[SUCCESS] Dashboard fully updated: Risk (I18:I22), Issues (H18:H22), Recommendations (L18:L34)")
            
        except Exception as dash_e:
            print(f"[WARNING] Could not update Dashboard summary: {dash_e}")
        
        print("\n" + "="*60)
        print("[SUCCESS] MODEL RUN COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        raise


@xw.sub
def run_model_from_excel():
    """
    Excel-callable function.
    """
    print("\n[MODEL] Model triggered from Excel")
    wb = xw.Book.caller()
    run_model(wb.fullname)

@xw.sub
def run_evaluation_from_excel():
    """
    Excel-callable function to run the model evaluation (MAE, MSE, R2, BIC).
    Writes results back to an 'Evaluation_Results' sheet.
    """
    import datetime
    print("\n[EVAL] Evaluation triggered from Excel")
    
    try:
        wb = xw.Book.caller()
        # Resolve history.csv relative to the workbook's location
        # CONSISTENT PATHING: history.csv is always in prediction_model/data/
        history_path = os.path.join(BASE_DIR, "data", "history.csv")
        
        # Run evaluation
        results = load_and_evaluate(history_path)
        
        if not results or results.get('MAE') is None:
             print("❌ Evaluation failed or no data available.")
             return

        # Prepare results for Excel
        eval_data = {
            "Metric": ["MAE", "MSE", "R2", "BIC", "Timestamp"],
            "Value": [
                round(results['MAE'], 4), 
                round(results['MSE'], 4), 
                round(results['R2'], 4), 
                round(results['BIC'], 4), 
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        df_eval = pd.DataFrame(eval_data)

        # Write to Output sheet instead of a new sheet
        sheet_name = OUTPUT_SHEET # Consolidate into Output
        if sheet_name in [s.name for s in wb.sheets]:
            sheet = wb.sheets[sheet_name]
            # Clear old evaluation area completely to wipe formatting
            sheet.range("I:Z").clear()
        else:
            sheet = wb.sheets.add(sheet_name)
        
        # Write metrics to a specific side-panel range (J2)
        print(f"Writing metrics to {sheet_name} [Range J2]...")
        sheet.range("J2").value = "--- MODEL PERFORMANCE ---"
        sheet.range("J2").font.bold = True
        try:
            sheet.range("J2:K2").merge()
            sheet.range("J2:K2").api.HorizontalAlignment = -4108 # Center
        except:
            pass
            
        sheet.range("J3").options(index=False).value = df_eval
        
        # Formatting for the metrics table
        sheet.range("J3:K3").font.bold = True
        sheet.range("J3:K3").color = (68, 114, 196) # Blue Header
        sheet.range("J3:K3").font.color = (255, 255, 255) # White Text
        
        # Set column widths
        sheet.range("I:I").column_width = 5  # Spacer
        sheet.range("J:K").column_width = 18
        
        print(f"[SUCCESS] Evaluation results written as a side-panel in {sheet_name}")
        
        # Optional: Bring sheet to focus
        sheet.activate()

    except Exception as e:
        error_msg = f"[ERROR] Error during Excel evaluation: {e}"
        print(error_msg)
        try:
            xw.Book.caller().app.api.MsgBox(error_msg)
        except:
            pass


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

