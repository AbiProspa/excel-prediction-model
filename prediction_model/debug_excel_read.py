import pandas as pd
import os

EXCEL_FILE = r"C:\Users\abiod\Documents\GitHub\scratch\prediction_model\data\Feedback_Dashboard_Template.xlsm"
SHEET_NAME = "Feedback_Data"

print(f"Reading file: {EXCEL_FILE}")
print(f"Sheet: {SHEET_NAME}")

if not os.path.exists(EXCEL_FILE):
    print("❌ File DOES NOT EXIST on disk!")
else:
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        print("\n--- RAW DATA FROM DISK (First 5 Rows) ---")
        print(df[['Feedback Type', 'Rating (1–5)', 'Comments']].head().to_string())
        print("-----------------------------------------")
        print(f"Total Rows: {len(df)}")
    except Exception as e:
        print(f"❌ Error reading excel: {e}")
