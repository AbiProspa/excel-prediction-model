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
        - Critical: Avg Rating ≤ 2 AND Strongly negative sentiment
        - Warning: Avg Rating ≈ 3 OR Mild negative sentiment
        - Stable: Avg Rating ≥ 4 AND Neutral/Positive sentiment
        """
        rating = row.get('Average Rating', 5)
        sentiment = row.get('Average Sentiment Score', 0)
        
        # Critical conditions
        if rating <= 2 and sentiment < -0.3:
            return "Critical"
        
        # Warning conditions
        if (rating > 2 and rating < 3.5) or (sentiment >= -0.3 and sentiment < 0):
            return "Warning"
            
        # Stable conditions
        if rating >= 4 and sentiment >= 0:
            return "Stable"
        
        # Default fallback logic for edge cases
        # Use a weighted scoring approach
        if rating <= 2.5:
            return "Critical"
        elif rating < 3.75:
            return "Warning"
        else:
            return "Stable"
    
    prob_df['Risk Level'] = prob_df.apply(get_risk_level, axis=1)
    
    print("Risk assessment complete.")
    return prob_df

