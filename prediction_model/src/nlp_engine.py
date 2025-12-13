import pandas as pd
from textblob import TextBlob

def analyze_comments(df):
    """
    Analyzes comments for sentiment and keywords.
    
    Args:
        df (pd.DataFrame): DataFrame containing 'Comments' column.
        
    Returns:
        pd.DataFrame: DataFrame with added 'Sentiment Score' and 'Keywords' columns.
    """
    if df.empty:
        return df
        
    if 'Comments' not in df.columns:
        print("Warning: 'Comments' column not found for NLP analysis.")
        df['Sentiment Score'] = 0.0
        df['Keywords'] = ""
        return df
    
    def get_sentiment(text):
        if pd.isna(text):
            return 0.0
        analysis = TextBlob(str(text))
        return analysis.sentiment.polarity

    def get_keywords(text):
        if pd.isna(text):
            return ""
        text = str(text).lower()
        keywords = []
        # Basic keyword extraction based on common banking issues
        trigger_words = [
            "network down", "failed", "slow", "crash", "down", "error", 
            "timeout", "rude", "wait", "charged", "refund", "login"
        ]
        
        for word in trigger_words:
            if word in text:
                keywords.append(word)
                
        return ", ".join(keywords)

    print("Calculating sentiment scores...")
    df['Sentiment Score'] = df['Comments'].apply(get_sentiment)
    
    print("Extracting keywords...")
    df['Keywords'] = df['Comments'].apply(get_keywords)
    
    # We no longer need to classify 'Feedback Type' as it is provided in the input
    
    return df
