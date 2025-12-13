import pandas as pd

def load_feedback_data(filepath):
    """
    Loads feedback data from an Excel file.
    
    Args:
        filepath (str): Path to the Excel file.
        
    Returns:
        pd.DataFrame: DataFrame containing the feedback data.
    """
    try:
        df = pd.read_excel(filepath, sheet_name='Feedback_Data')
        # Rename columns to match expected format
        # Rename columns to match expected format
        df = df.rename(columns={
            'Feedback Type': 'Product',
            'Rating (1–5)': 'Rating',
            'Comments': 'Comment'
        })
        # Keep only needed columns
        df = df[['Date', 'Customer', 'Product', 'Rating', 'Comment', 'Status']]
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()
