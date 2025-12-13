import pandas as pd

def assess_risk(prob_df):
    """
    Assess risk based on probability thresholds.
    
    Args:
        prob_df (pd.DataFrame): DataFrame with probabilities.
        
    Returns:
        pd.DataFrame: DataFrame with 'Risk Level' column.
    """
    if prob_df.empty:
        return prob_df
    
    def get_risk_level(row):
        # Thresholds
        thresholds = {
            'Availability': {'Warning': 0.40, 'Critical': 0.60},
            'Transaction Success': {'Warning': 0.35, 'Critical': 0.55},
            'Satisfaction': {'Warning': 0.30, 'Critical': 0.50}
        }
        
        risk_level = "Stable"
        
        # Check Availability
        if row.get('Probability of Availability Issues', 0) > thresholds['Availability']['Critical']:
            return "Critical Risk"
        if row.get('Probability of Availability Issues', 0) > thresholds['Availability']['Warning']:
            risk_level = "Warning"
            
        # Check Transaction Success
        if row.get('Probability of Transaction Success Issues', 0) > thresholds['Transaction Success']['Critical']:
            return "Critical Risk"
        if row.get('Probability of Transaction Success Issues', 0) > thresholds['Transaction Success']['Warning']:
            risk_level = "Warning"
            
        # Check Satisfaction
        if row.get('Probability of Satisfaction Issues', 0) > thresholds['Satisfaction']['Critical']:
            return "Critical Risk"
        if row.get('Probability of Satisfaction Issues', 0) > thresholds['Satisfaction']['Warning']:
            risk_level = "Warning"
            
        return risk_level

    prob_df['Risk Level'] = prob_df.apply(get_risk_level, axis=1)
    return prob_df
