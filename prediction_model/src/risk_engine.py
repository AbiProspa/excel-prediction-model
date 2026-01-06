import pandas as pd

def assess_risk(prob_df):
    """
    Assess risk level based on Average Rating and Sentiment Score.
    
    Args:
        prob_df (pd.DataFrame): DataFrame with 'Average Rating' and 'Average Sentiment Score'.
        
    Returns:
        pd.DataFrame: DataFrame with 'Risk Level' column added.
    """
    if prob_df.empty:
        return prob_df
    
    print("Assessing risk levels...")
    
    def get_risk_level(row):
        """
        Determine risk level based on:
        - Critical: Avg Rating <= 2 OR Very High Negative Sentiment (> 0.7)
        - Warning: Avg Rating < 4 OR Moderate Negative Sentiment (> 0.4)
        - Stable: High Rating (>= 4) AND Low Negative Sentiment (<= 0.4)
        """
        rating = row.get('Average Rating', 5)
        # BERT Sentiment is "Probability of Negativity" (0.0 = Positive/Neutral, 1.0 = Highly Negative)
        neg_prob = row.get('Average Sentiment Score', 0)
        
        # 1. Critical Logic
        # - Extremely low rating (1-2 stars)
        # - OR Significant conflict: OK rating (3) but Terrible Sentiment (0.8+)
        if rating <= 2.5 or (rating <= 3.5 and neg_prob > 0.8):
            return "Critical"
        
        # 2. Warning Logic
        # - Mediocre rating (3 stars)
        # - OR Mildly negative sentiment (0.4 - 0.7) even with good stars
        if rating < 4.0 or neg_prob > 0.4:
            return "Warning"
            
        # 3. Stable Logic
        # - Good rating (4-5) AND Low negative sentiment (< 0.4)
        return "Stable"
    
    prob_df['Risk Level'] = prob_df.apply(get_risk_level, axis=1)
    
    print("Risk assessment complete.")
    return prob_df

