import pandas as pd
import os

def load_feedback_data(excel_path, sheet_name="Feedback_Data"):
    """
    Loads feedback data from a specific Excel sheet and validates structure.
    
    Args:
        excel_path (str): Path to the Excel file.
        sheet_name (str): Name of the sheet to read.
        
    Returns:
        pd.DataFrame: DataFrame containing the feedback data.
    """
    required_columns = [
        'Date', 'Customer', 'Feedback Type', 'Rating (1–5)', 
        'Status', 'Follow-Up', 'Comments'
    ]

    print(f"Loading data from {excel_path} [{sheet_name}]...")

    if not os.path.exists(excel_path):
        print(f"Error: File not found at {excel_path}")
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    try:
        # Read the Excel file
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # Validate columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            error_msg = f"Missing required columns in '{sheet_name}': {missing_cols}"
            print(error_msg)
            raise ValueError(error_msg)
            
        # Minimal data cleaning
        df = df.dropna(how='all') # Drop completely empty rows
        
        print(f"Successfully loaded {len(df)} rows.")
        return df

    except ValueError as ve:
        # Sheet missing or columns missing
        print(f"Data Validation Error: {ve}")
        raise
    except Exception as e:
        print(f"Unexpected error loading data: {e}")
        raise
