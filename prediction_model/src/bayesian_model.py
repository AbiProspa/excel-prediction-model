import pandas as pd
from learning_engine import load_weights

def calculate_probabilities(df):
    """
    Groups data by 'Feedback Type' and computes probability scores based on
    rating distribution and sentiment severity using ADAPTIVE WEIGHTS.
    
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
    
    # Rename columns to match Risk Engine expectations
    grouped.rename(columns={
        'Rating': 'Average Rating',
        'Sentiment Score': 'Average Sentiment Score'
    }, inplace=True)
    
    # 2. Compute Probability Score
    weights = load_weights()
    print(f"Using Adaptive Weights: {weights}")
    
    # Normalize Rating (1-5) to 0-1 (Issue Prob)
    # 1 -> 1.0, 5 -> 0.0
    grouped['Rating Prob'] = (5 - grouped['Average Rating']) / 4
    
    # Normalize Sentiment from BERT (0.0 - 1.0 negative prob) to 0-1 (Issue Prob)
    # BERT output is already "Negative Probability", so logic changes from existing code!
    # Validating BERT output nature: `get_negative_probability` returns 0.0 to 1.0 (Prob of Negative).
    # So 0.9 = Very Negative = High Issue Prob.
    # Existing code assumed Sentiment Score was -1 to 1 (Polarity).
    # New code uses 'Average Sentiment Score' which is mean(BERT Negative Prob).
    # So 'Average Sentiment Score' is ALREADY the 'Sentiment Prob'.
    grouped['Sentiment Prob'] = grouped['Average Sentiment Score']
    
    # Combined Probability Score (Weighted Average)
    # Final = w1 * rating_prob + w2 * sentiment_prob
    if 'rating_weight' in weights and 'sentiment_weight' in weights:
        grouped['Probability Score'] = (
            weights['rating_weight'] * grouped['Rating Prob'] +
            weights['sentiment_weight'] * grouped['Sentiment Prob']
        )
    else:
        # Fallback to simple average
        grouped['Probability Score'] = (grouped['Rating Prob'] + grouped['Sentiment Prob']) / 2
    
    # Clip to 0-1 range just in case
    grouped['Probability Score'] = grouped['Probability Score'].clip(0, 1)
    
    print("Probability calculation complete.")
    return grouped
