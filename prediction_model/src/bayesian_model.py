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
    # Define aggregation help
    def summarize_keywords(series):
        # Join all text
        all_text = ' '.join([str(k) for k in series if k])
        # Split by comma or space
        words = [w.strip() for w in all_text.replace(',', ' ').split() if w.strip()]
        # Unique only
        unique_words = sorted(list(set(words)))
        return ", ".join(unique_words)

    agg_funcs = {
        'Rating': 'mean',
        'Sentiment Score': 'mean',
        'Keywords': summarize_keywords
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
    
    # Keyword Priors: High-impact words boost the Sentiment Prob
    KEYWORD_PRIORS = {
        "crash": 0.95,
        "failed": 0.9,
        "broken": 0.9,
        "fraud": 0.95,
        "down": 0.85,
        "terrible": 0.85,
        "error": 0.8
    }

    def boost_sentiment(row):
        base_prob = row['Average Sentiment Score']
        keywords = str(row.get('Keywords', '')).lower().split(', ')
        
        boosts = [KEYWORD_PRIORS[k] for k in keywords if k in KEYWORD_PRIORS]
        if boosts:
            # If high-risk keywords exist, we lean heavily towards their prior
            return max(base_prob, max(boosts))
        return base_prob

    # Normalize Rating (1-5) to 0-1 (Issue Prob)
    # 1 -> 1.0, 5 -> 0.0
    grouped['Rating Prob'] = (5 - grouped['Average Rating']) / 4
    
    # Calculate Boosted Sentiment Prob
    grouped['Sentiment Prob'] = grouped.apply(boost_sentiment, axis=1)
    
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
