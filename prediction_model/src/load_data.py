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
        'Product': ['product', 'item', 'category', 'feedback type'], 
        'SubCategory': ['subtype', 'sub-type'], 
        'Rating': ['rating', 'score', 'ratings'],
        'Comment': ['comment', 'comments', 'feedback text', 'text'],
        'Status': ['status', 'state']
    }
    
    CORE_SERVICES = ['ATM', 'Online Banking', 'App', 'Service', 'Loan Process']

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
            # Use used_range instead of expand() to gracefully handle blank rows/columns
            df = sht.used_range.options(pd.DataFrame, index=False).value
            print(f"[SUCCESS] Connected live to {wb.name}")
            
        except Exception as live_e:
            print(f"[WARNING] Live connection unavailable or blocked by Edit Mode. Falling back to saved file...")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # 2. Fuzzy Header Mapping (New robust logic)
        actual_cols = df.columns.tolist()
        normalized_actual = [str(c).strip().lower() for c in actual_cols]
        new_columns = {}
        mapped_indices = set()
        missing = []

        # Pass 1: Exact Matches
        for canonical, aliases in REQUIRED_MAP.items():
            low_can = canonical.lower()
            if low_can in normalized_actual:
                idx = normalized_actual.index(low_can)
                new_columns[actual_cols[idx]] = canonical
                mapped_indices.add(idx)

        # Pass 2: Alias/Partial Matches
        for canonical, aliases in REQUIRED_MAP.items():
            if canonical in new_columns.values():
                continue # Already found exact match
            
            found = False
            for alias in aliases:
                for i, act in enumerate(normalized_actual):
                    if i in mapped_indices: continue
                    if alias in act or act in alias:
                        new_columns[actual_cols[i]] = canonical
                        mapped_indices.add(i)
                        found = True
                        break
                if found: break
            
            if not found:
                missing.append(canonical)

        # Manage missing columns (SubCategory is now optional)
        OPTIONAL = ['SubCategory']
        critical_missing = [m for m in missing if m not in OPTIONAL]
        
        if critical_missing:
            found_cols = [df.columns.tolist()]
            print(f"[ERROR] FOUND COLUMNS: {found_cols}")
            error_msg = f"Missing required columns in '{sheet_name}': {critical_missing}.\nWe found these columns instead: {found_cols}"
            print(f"[ERROR] {error_msg}")
            raise ValueError(error_msg)

        # Rename columns to their canonical names
        df = df.rename(columns=new_columns)
        
        # Add missing optional columns
        for opt in OPTIONAL:
            if opt not in df.columns:
                df[opt] = "General"
        
        # Maintain compatibility: Rename SubCategory back to Feedback Type for the model
        df = df.rename(columns={'SubCategory': 'Feedback Type'})
        
        # Keep only the ones we need for the model
        expected_cols = ['Date', 'Product', 'Feedback Type', 'Rating', 'Comment', 'Status']
        df = df[expected_cols]
        
        # 3. Minimal data cleaning
        df = df.dropna(how='all') 
        
        # 4. Strict Category Filter (ATM, Online Banking, App, Service, Loan Process)
        if 'Product' in df.columns:
            initial_count = len(df)
            df = df[df['Product'].isin(CORE_SERVICES)]
            lost = initial_count - len(df)
            if lost > 0:
                print(f"[INFO] Filtered out {lost} rows not belonging to core services.")
        
        print(f"[SUCCESS] Successfully loaded {len(df)} rows after service filtering.")
        return df

    except Exception as e:
        print(f"Unexpected error loading data: {e}")
        raise
