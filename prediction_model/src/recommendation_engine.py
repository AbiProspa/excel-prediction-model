import pandas as pd

def generate_recommendations(risk_df):
    """
    Generates business-actionable recommendations based on Risk Level and Feedback Type.
    
    Args:
        risk_df (pd.DataFrame): DataFrame with 'Risk Level', 'Feedback Type', 'Keywords'.
        
    Returns:
        pd.DataFrame: DataFrame with 'Top Issue Summary' and 'Recommendation' columns.
    """
    if risk_df.empty:
        return risk_df
    
    print("Generating recommendations...")
    
    # Recommendation mapping based on Feedback Type and Risk Level
    recommendations = {
        "Critical": {
            "default": "Immediate investigation required. Escalate to senior management and deploy dedicated resources."
        },
        "Warning": {
            "default": "Improve follow-up process and monitor trends closely. Schedule review within 2 weeks."
        },
        "Stable": {
            "default": "Continue current monitoring practices. Maintain quality standards."
        }
    }
    
    # Specific recommendations by Feedback Type
    specific_recs = {
        "ATM": {
            "Critical": "Immediate maintenance required for ATM network. Check for hardware failures and cash availability.",
            "Warning": "Increase ATM cash replenishment frequency. Schedule preventive maintenance.",
            "Stable": "ATM network operating normally. Continue regular maintenance schedule."
        },
        "POS": {
            "Critical": "Critical POS terminal issues detected. Deploy technical team for urgent repairs.",
            "Warning": "Monitor POS transaction success rates. Update firmware if necessary.",
            "Stable": "POS terminals functioning well. Maintain current support levels."
        },
        "Mobile App": {
            "Critical": "App experiencing critical issues. Roll back recent updates and investigate server capacity.",
            "Warning": "Address app performance concerns. Conduct user testing and optimize load times.",
            "Stable": "Mobile app performance is satisfactory. Continue feature enhancements."
        },
        "Online Banking": {
            "Critical": "Critical online banking issues. Check server status and security protocols immediately.",
            "Warning": "Improve online banking user experience. Address login and navigation issues.",
            "Stable": "Online banking service running smoothly. Monitor for security threats."
        },
        "Customer Service": {
            "Critical": "Immediate customer service improvements needed. Increase staffing and conduct training.",
            "Warning": "Enhance customer service processes. Reduce wait times and improve staff responsiveness.",
            "Stable": "Customer service performing well. Maintain current service quality."
        },
        "Loan Services": {
            "Critical": "Critical issues in loan processing. Streamline approval process and fix system bugs.",
            "Warning": "Improve loan application processing times. Clarify documentation requirements.",
            "Stable": "Loan services meeting expectations. Continue efficient processing."
        }
    }
    
    def extract_top_issues(keywords_str):
        """Extract top 3 most mentioned keywords"""
        if pd.isna(keywords_str) or not keywords_str:
            return "No specific issues identified"
        
        # Split and count keywords
        keywords = [k.strip() for k in str(keywords_str).split(',') if k.strip()]
        if not keywords:
            return "General feedback"
        
        # Simple frequency count
        keyword_freq = {}
        for kw in keywords:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
        
        # Get top 3
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        top_issue_text = ", ".join([k for k, v in top_keywords])
        
        return top_issue_text if top_issue_text else "General concerns"
    
    def get_recommendation(row):
        feedback_type = row.get('Feedback Type', 'Unknown')
        risk_level = row.get('Risk Level', 'Stable')
        keywords = row.get('Keywords', '')
        
        # Get specific recommendation
        if feedback_type in specific_recs and risk_level in specific_recs[feedback_type]:
            rec = specific_recs[feedback_type][risk_level]
        else:
            rec = recommendations.get(risk_level, {}).get('default', 
                                                           'Monitor situation and take appropriate action.')
        
        # Extract top issues
        top_issue = extract_top_issues(keywords)
        
        return pd.Series([top_issue, rec])
    
    risk_df[['Top Issue Summary', 'Recommendation']] = risk_df.apply(get_recommendation, axis=1)
    
    print("Recommendations generated.")
    return risk_df
