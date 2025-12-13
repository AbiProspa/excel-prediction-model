import pandas as pd

def generate_recommendations(risk_df):
    """
    Generates recommendations based on the top issue.
    
    Args:
        risk_df (pd.DataFrame): DataFrame with probabilities and risk levels.
        
    Returns:
        pd.DataFrame: DataFrame with 'Top Issue', 'Probability of Top Issue', and 'Suggested Recommendation'.
    """
    if risk_df.empty:
        return risk_df
        
    recommendations = {
        "ATM": {
            "Availability": "Schedule preventive maintenance for cash dispenser and card reader. Ensure regular cash replenishment cycles.",
            "Transaction Success": "Inspect card reader for physical faults. Check network connectivity and switch stability.",
            "Satisfaction": "Ensure ATM area is clean and well-lit. Review user interface for clarity and ease of use."
        },
        "App": {
            "Availability": "Investigate server uptime and API response times. Implement auto-scaling for peak loads.",
            "Transaction Success": "Optimize API endpoints for faster processing. Improve error handling and retry mechanisms.",
            "Satisfaction": "Conduct user testing to identify UX pain points. Simplify navigation and improve app performance."
        },
        "Online Banking": {
            "Availability": "Monitor web server load and database performance. Optimize database queries.",
            "Transaction Success": "Enhance session management and security protocols. Check for browser compatibility issues.",
            "Satisfaction": "Streamline the login process. Improve dashboard layout and feature accessibility."
        },
        "Loan Process": {
            "Availability": "Ensure loan processing system is accessible during business hours. Check integration with credit bureaus.",
            "Transaction Success": "Simplify document upload process. Fix bugs in the application form submission.",
            "Satisfaction": "Reduce approval turnaround time. Provide clear status updates to applicants."
        },
        "Service": {
            "Availability": "Ensure adequate staff coverage during peak hours. Reduce wait times.",
            "Transaction Success": "Train staff on efficient query resolution. Empower staff to make decisions.",
            "Satisfaction": "Conduct customer service training. Implement a feedback loop for continuous improvement."
        }
    }
    
    def get_recommendation(row):
        product = row['Product']
        
        # Identify top issue
        issues = {
            'Availability': row.get('Probability of Availability Issues', 0),
            'Transaction Success': row.get('Probability of Transaction Success Issues', 0),
            'Satisfaction': row.get('Probability of Satisfaction Issues', 0)
        }
        
        top_issue = max(issues, key=issues.get)
        prob_top_issue = issues[top_issue]
        
        # Get specific recommendation
        product_recs = recommendations.get(product, {})
        rec = product_recs.get(top_issue, "No specific recommendation available for this product/issue.")
        
        return pd.Series([top_issue, prob_top_issue, rec])

    risk_df[['Top Issue', 'Probability of Top Issue', 'Suggested Recommendation']] = risk_df.apply(get_recommendation, axis=1)
    
    return risk_df
