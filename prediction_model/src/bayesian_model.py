import pandas as pd

def calculate_probabilities(df):
    """
    Groups data by 'Feedback Type' and computes probability scores based on
    rating distribution and sentiment severity.
    
    Args:
        df (pd.DataFrame): DataFrame containing 'Feedback Type', 'Rating', 'Sentiment Score'.
        
    Returns:
        pd.DataFrame: Aggregated DataFrame with probability scores.
    """
    if df.empty:
        return pd.DataFrame()

    print("Aggregating data by Feedback Type...")
    
    # 1. Group by Feedback Type
    # Convert Rating to numeric just in case
    rating_col = 'Rating (1–5)'
    df['Rating'] = pd.to_numeric(df[rating_col], errors='coerce')
    
    # Define aggregation
    agg_funcs = {
        'Rating': 'mean',
        'Sentiment Score': 'mean',
        'Keywords': lambda x: ' '.join([str(k) for k in x if k]) # Collect all keywords
    }
    
    grouped = df.groupby('Feedback Type').agg(agg_funcs).reset_index()
    
    # Rename columns
    grouped.rename(columns={
        'Rating': 'Average Rating',
        'Sentiment Score': 'Average Sentiment Score' # Renamed to avoid confusion with raw scores
    }, inplace=True)
    
    # 2. Compute Probability Score
    # Logic: 
    # Low Rating -> High Probability of Issue
    # Negative Sentiment -> High Probability of Issue
    
    # Normalize Rating (1-5) to 0-1 (Issue Prob)
    # 1 -> 1.0, 5 -> 0.0
    # Formula: (5 - Rating) / 4
    grouped['Rating Prob'] = (5 - grouped['Average Rating']) / 4
    
    # Normalize Sentiment (-1 to 1) to 0-1 (Issue Prob)
    # -1 -> 1.0, 1 -> 0.0
    # Formula: (1 - Sentiment) / 2
    grouped['Sentiment Prob'] = (1 - grouped['Average Sentiment Score']) / 2
    
    # Combined Probability Score (Average of both)
    grouped['Probability Score'] = (grouped['Rating Prob'] + grouped['Sentiment Prob']) / 2
    
    # Clip to 0-1 range just in case
    grouped['Probability Score'] = grouped['Probability Score'].clip(0, 1)
    
    print("Probability calculation complete.")
    return grouped
