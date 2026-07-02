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
from compare_benchmarks import compare_models

# ========================================
# CENTRALIZED EXCEL CONFIGURATION
# ========================================
# Use relative path for portability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE_PATH = os.path.join(BASE_DIR, "data", "Feedback_Dashboard_Template.xlsm")
INPUT_SHEET = "Feedback_Data"
OUTPUT_SHEET = "Output"
CORE_SERVICES = ['App', 'ATM', 'Loan Process', 'Online Banking', 'Service']


def _find_open_workbook(excel_path):
    target_path = os.path.abspath(excel_path).lower()

    try:
        caller = xw.Book.caller()
        if caller.fullname and caller.fullname.lower() == target_path:
            return caller
    except Exception:
        pass

    for app in xw.apps:
        for book in app.books:
            try:
                if book.fullname and book.fullname.lower() == target_path:
                    return book
            except Exception:
                continue

    return xw.Book(excel_path)


def _safe_chart(dashboard, chart_name):
    try:
        return dashboard.api.ChartObjects(chart_name).Chart
    except Exception as exc:
        print(f"[WARNING] Dashboard chart '{chart_name}' was not found: {exc}")
        return None


def _set_series_formula(series, name, categories_range, values_range, order):
    formula = (
        f'=SERIES("{name}",'
        f"'{categories_range.sheet.name}'!{categories_range.get_address(False, False)},"
        f"'{values_range.sheet.name}'!{values_range.get_address(False, False)},"
        f"{order})"
    )
    series.Formula = formula


def update_dashboard_charts(wb, df):
    """
    Rebuilds the worksheet-backed dashboard chart data and points the existing
    dashboard charts at those ranges. The template charts were originally saved
    with literal cached values, so Excel had no source ranges to recalculate.
    """
    if df.empty:
        print("[WARNING] Dashboard charts not updated because no feedback rows were loaded.")
        return

    dashboard = wb.sheets['Dashboard']
    sheet_name = "Dashboard_Data"

    if sheet_name in [sheet.name for sheet in wb.sheets]:
        chart_data = wb.sheets[sheet_name]
        chart_data.clear()
    else:
        chart_data = wb.sheets.add(sheet_name, after=wb.sheets[-1])

    chart_data.visible = False

    chart_df = df.copy()
    chart_df['Rating'] = pd.to_numeric(chart_df['Rating'], errors='coerce')
    chart_df['Date'] = pd.to_datetime(chart_df['Date'], errors='coerce')
    chart_df['Status'] = chart_df['Status'].astype(str).str.strip()

    categories = CORE_SERVICES
    type_counts = chart_df['Product'].value_counts().reindex(categories, fill_value=0)
    rating_sums = chart_df.groupby('Product')['Rating'].sum().reindex(categories, fill_value=0)

    rating_table = (
        chart_df.pivot_table(
            index='Product',
            columns='Rating',
            values='Status',
            aggfunc='count',
            fill_value=0,
        )
        .reindex(index=categories, fill_value=0)
        .reindex(columns=[1, 2, 3, 4, 5], fill_value=0)
    )

    status_table = pd.DataFrame({
        "Open": chart_df.assign(
            DashboardStatus=chart_df['Status'].where(
                chart_df['Status'].str.lower().eq('resolved'),
                'Open',
            )
        ).query("DashboardStatus == 'Open'")['Product'].value_counts().reindex(categories, fill_value=0),
        "Resolved": chart_df[chart_df['Status'].str.lower().eq('resolved')]['Product']
            .value_counts()
            .reindex(categories, fill_value=0),
    })

    monthly_counts = (
        chart_df.dropna(subset=['Date'])
        .groupby(chart_df.dropna(subset=['Date'])['Date'].dt.to_period('M'))
        .size()
        .tail(6)
    )
    if monthly_counts.empty:
        monthly_labels = ["No Date"]
        monthly_values = [0]
    else:
        monthly_labels = [period.strftime('%b %Y') for period in monthly_counts.index]
        monthly_values = monthly_counts.astype(int).tolist()

    chart_data.range("A1").value = "Feedback Type Distribution"
    chart_data.range("A2:B2").value = [["Feedback Type", "Count"]]
    chart_data.range("A3").options(index=False, header=False).value = [
        [category, int(type_counts.loc[category])] for category in categories
    ]

    chart_data.range("D1").value = "Rating by Feedback"
    chart_data.range("D2:E2").value = [["Feedback Type", "Total Rating"]]
    chart_data.range("D3").options(index=False, header=False).value = [
        [category, float(rating_sums.loc[category])] for category in categories
    ]

    chart_data.range("G1").value = "Feedback Rating"
    chart_data.range("G2:L2").value = [["Feedback Type", 1, 2, 3, 4, 5]]
    chart_data.range("G3").options(index=False, header=False).value = [
        [category, *[int(rating_table.loc[category, rating]) for rating in [1, 2, 3, 4, 5]]]
        for category in categories
    ]

    chart_data.range("N1").value = "Feedback Over Time"
    chart_data.range("N2:O2").value = [["Month", "Total"]]
    chart_data.range("N3").options(index=False, header=False).value = list(zip(monthly_labels, monthly_values))

    chart_data.range("Q1").value = "Status Count"
    chart_data.range("Q2:S2").value = [["Feedback Type", "Open", "Resolved"]]
    chart_data.range("Q3").options(index=False, header=False).value = [
        [
            category,
            int(status_table.loc[category, "Open"]),
            int(status_table.loc[category, "Resolved"]),
        ]
        for category in categories
    ]

    chart_data.autofit('c')

    pie_chart = _safe_chart(dashboard, "Chart 1")
    if pie_chart:
        _set_series_formula(
            pie_chart.SeriesCollection(1),
            "Total",
            chart_data.range("A3:A7"),
            chart_data.range("B3:B7"),
            1,
        )

    bar_chart = _safe_chart(dashboard, "Chart 3")
    if bar_chart:
        _set_series_formula(
            bar_chart.SeriesCollection(1),
            "Total",
            chart_data.range("D3:D7"),
            chart_data.range("E3:E7"),
            1,
        )

    rating_chart = _safe_chart(dashboard, "Chart 29")
    if rating_chart:
        for idx, rating in enumerate([1, 2, 3, 4, 5], start=1):
            _set_series_formula(
                rating_chart.SeriesCollection(idx),
                str(rating),
                chart_data.range("G3:G7"),
                chart_data.range((3, 7 + idx), (7, 7 + idx)),
                idx,
            )

    time_chart = _safe_chart(dashboard, "Chart 30")
    if time_chart:
        last_row = 2 + len(monthly_labels)
        _set_series_formula(
            time_chart.SeriesCollection(1),
            "Total",
            chart_data.range(f"N3:N{last_row}"),
            chart_data.range(f"O3:O{last_row}"),
            1,
        )

    status_chart = _safe_chart(dashboard, "Chart 31")
    if status_chart:
        _set_series_formula(
            status_chart.SeriesCollection(1),
            "Open",
            chart_data.range("Q3:Q7"),
            chart_data.range("R3:R7"),
            1,
        )
        _set_series_formula(
            status_chart.SeriesCollection(2),
            "Resolved",
            chart_data.range("Q3:Q7"),
            chart_data.range("S3:S7"),
            2,
        )

    try:
        wb.app.api.CalculateFullRebuild()
    except Exception:
        pass

    print("[SUCCESS] Dashboard charts refreshed from Dashboard_Data.")


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
            wb = _find_open_workbook(excel_path)
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
                    
            update_dashboard_charts(wb, df)

            try:
                wb.save()
            except Exception as save_e:
                print(f"[WARNING] Dashboard updated but workbook could not be saved automatically: {save_e}")

            print(f"[SUCCESS] Dashboard fully updated: charts, Risk (I18:I22), Issues (H18:H22), Recommendations (L18:L34)")
            
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
             print("Evaluation failed or no data available.")
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
            sheet.range("I:K").clear()
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

@xw.sub
def run_benchmark_from_excel():
    """
    Excel-callable function to compare Bayesian-BERT against benchmark models.
    Writes a presentation-friendly table into the workbook.
    """
    print("\n[BENCHMARK] Benchmark comparison triggered from Excel")

    try:
        wb = xw.Book.caller()
        history_path = os.path.join(BASE_DIR, "data", "history.csv")
        output_path = os.path.join(BASE_DIR, "data", "benchmark_comparison.csv")

        comparison, saved_path, train_count, test_count = compare_models(
            history_path,
            output_path,
        )

        display_cols = ["Model", "Accuracy", "Precision", "Recall", "F1-score"]
        display_df = comparison[display_cols].copy()
        for col in display_cols[1:]:
            display_df[col] = (display_df[col] * 100).round(1).astype(str) + "%"

        full_df = comparison.copy()

        sheet_name = "Benchmark_Comparison"
        if sheet_name in [s.name for s in wb.sheets]:
            sheet = wb.sheets[sheet_name]
            sheet.clear()
        else:
            sheet = wb.sheets.add(sheet_name, after=wb.sheets[-1])

        sheet.range("A1").value = "MODEL BENCHMARK COMPARISON"
        sheet.range("A1").font.bold = True
        sheet.range("A1").font.size = 16

        sheet.range("A3").value = "Presentation Table"
        sheet.range("A3").font.bold = True
        sheet.range("A4").options(index=False).value = display_df

        sheet.range("A10").value = "Full Metrics"
        sheet.range("A10").font.bold = True
        sheet.range("A11").options(index=False).value = full_df

        sheet.range("A18").value = "Notes"
        sheet.range("A18").font.bold = True
        sheet.range("A19").value = (
            f"Training rows: {train_count}; Test rows: {test_count}. "
            "RIC is Risk Identification Correctness, implemented as balanced accuracy."
        )
        sheet.range("A20").value = f"CSV saved to: {saved_path}"

        sheet.range("A4:E4").font.bold = True
        sheet.range("A4:E4").color = (68, 114, 196)
        sheet.range("A4:E4").font.color = (255, 255, 255)
        sheet.range("A11:I11").font.bold = True
        sheet.range("A11:I11").color = (68, 114, 196)
        sheet.range("A11:I11").font.color = (255, 255, 255)
        sheet.range("A:E").column_width = 18
        sheet.range("A:A").column_width = 24
        sheet.range("A19:I20").wrap_text = True

        try:
            sheet.range("A4:E8").api.Borders.Weight = 2
            sheet.range("A11:I15").api.Borders.Weight = 2
        except:
            pass

        output_sheet_name = OUTPUT_SHEET
        if output_sheet_name in [s.name for s in wb.sheets]:
            out_sheet = wb.sheets[output_sheet_name]
        else:
            out_sheet = wb.sheets.add(output_sheet_name)

        out_sheet.range("M:Q").clear()
        out_sheet.range("M2").value = "BENCHMARK COMPARISON"
        out_sheet.range("M2").font.bold = True
        out_sheet.range("M2").font.size = 14
        out_sheet.range("M4").options(index=False).value = display_df
        out_sheet.range("M4:Q4").font.bold = True
        out_sheet.range("M4:Q4").color = (68, 114, 196)
        out_sheet.range("M4:Q4").font.color = (255, 255, 255)
        out_sheet.range("M:Q").column_width = 18

        sheet.activate()
        print(f"[SUCCESS] Benchmark comparison written to '{sheet_name}' and '{output_sheet_name}'.")

    except Exception as e:
        error_msg = f"[ERROR] Error during benchmark comparison: {e}"
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
