import pandas as pd
from textblob import TextBlob

def analyze_comments(df):
    """
    Analyzes comments for sentiment and keywords.
    
    Args:
        df (pd.DataFrame): DataFrame containing 'Comment' column.
        
    Returns:
        pd.DataFrame: DataFrame with added 'Sentiment Score', 'Sentiment', and 'Keywords' columns.
    """
    if df.empty or 'Comment' not in df.columns:
        return df
    
    def get_sentiment(text):
        analysis = TextBlob(str(text))
        return analysis.sentiment.polarity

    def get_keywords(text):
        text = str(text).lower()
        keywords = []
        if "network down" in text: keywords.append("network down")
        if "failed" in text: keywords.append("failed")
        if "slow" in text: keywords.append("slow")
        if "crash" in text: keywords.append("crash")
        if "down" in text: keywords.append("down")
        return ", ".join(keywords)

    def classify_issue(row):
        text = str(row['Comment']).lower()
        keywords = str(row['Keywords']).lower()
        
        # Availability
        if any(x in text for x in ['crash', 'down', 'network', 'outage', 'unavailable']) or \
           any(x in keywords for x in ['crash', 'down', 'network']):
            return 'Availability'
            
        # Transaction Success
        if any(x in text for x in ['slow', 'fail', 'error', 'decline', 'reject', 'timeout']) or \
           any(x in keywords for x in ['slow', 'failed']):
            return 'Transaction Success'
            
        # Satisfaction (Default or specific keywords)
        if any(x in text for x in ['great', 'good', 'bad', 'helpful', 'service', 'staff', 'rude']):
            return 'Satisfaction'
            
        return 'Satisfaction' # Default

    df['Sentiment Score'] = df['Comment'].apply(get_sentiment)
    df['Sentiment'] = df['Sentiment Score'].apply(lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))
    df['Keywords'] = df['Comment'].apply(get_keywords)
    df['Feedback Type'] = df.apply(classify_issue, axis=1)
    
    return df
