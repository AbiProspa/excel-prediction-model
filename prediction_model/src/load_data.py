import pandas as pd
import os
import xlwings as xw

def load_feedback_data(excel_path, sheet_name="Feedback_Data"):
    """
    Loads feedback data from a specific Excel sheet and validates structure.
    Uses fuzzy matching for column headers to be robust against Excel formatting.
    """
    # Canonical names the model expects
    REQUIRED_MAP = {
        'Date': ['date', 'time', 'timestamp'],
        'Product': ['product', 'item', 'category'],
        'Feedback Type': ['feedback type', 'type', 'feedback'],
        'Rating': ['rating', 'score', 'ratings'],
        'Comment': ['comment', 'comments', 'feedback text', 'text'],
        'Status': ['status', 'state']
    }

    print(f"Loading data from {excel_path} [{sheet_name}]...")

    if not os.path.exists(excel_path):
        print(f"Error: File not found at {excel_path}")
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    try:
        # 1. Try Live Connection first (avoids "File in Use" locks)
        try:
            try:
                wb = xw.Book.caller()
            except:
                wb = xw.books.active
            
            if wb.fullname.lower() != os.path.abspath(excel_path).lower():
                 wb = xw.Book(excel_path)
            
            sht = wb.sheets[sheet_name]
            # Read everything starting from A1
            df = sht.range("A1").expand().options(pd.DataFrame, index=False).value
            print(f"✓ Connected live to {wb.name}")
            
        except Exception as live_e:
            print(f"⚠️ Live connection unavailable. Falling back to file read...")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # 2. Fuzzy Header Mapping
        actual_cols = [str(c).strip().lower() for c in df.columns]
        new_columns = {}
        missing = []

        for canonical, aliases in REQUIRED_MAP.items():
            found = False
            # Check for exact matches first
            if canonical.lower() in actual_cols:
                idx = actual_cols.index(canonical.lower())
                new_columns[df.columns[idx]] = canonical
                found = True
            else:
                # Check for aliases or substrings
                for alias in aliases:
                    for i, act in enumerate(actual_cols):
                        if alias in act or act in alias:
                            new_columns[df.columns[i]] = canonical
                            found = True
                            break
                    if found: break
            
            if not found:
                missing.append(canonical)

        if missing:
            print(f"❌ FOUND COLUMNS: {list(df.columns)}")
            error_msg = f"Missing required columns in '{sheet_name}': {missing}"
            print(f"❌ {error_msg}")
            raise ValueError(error_msg)

        # Rename columns to their canonical names
        df = df.rename(columns=new_columns)
        
        # Keep only the ones we need for the model
        df = df[list(REQUIRED_MAP.keys())]
        
        # 3. Minimal data cleaning
        df = df.dropna(how='all') 
        
        print(f"✓ Successfully loaded {len(df)} rows with fuzzy header mapping.")
        return df

    except Exception as e:
        print(f"Unexpected error loading data: {e}")
        raise
