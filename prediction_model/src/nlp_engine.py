from bert_sentiment import get_negative_probability

TRIGGER_WORDS = [
    "network", "failed", "slow", "crash",
    "timeout", "rude", "delay", "error",
    "cannot", "issue", "problem", "wait", "charged", "refund", "login",
    "broken", "horrible", "fraud", "stuck", "useless", "down", "terrible"
]

def extract_keywords(text):
    if not text:
        return []
    text = str(text).lower()
    return [word for word in TRIGGER_WORDS if word in text]

def analyze_comment(comment):
    """
    Analyzes a single comment for sentiment and keywords.
    """
    sentiment_prob = get_negative_probability(comment)
    keywords = extract_keywords(comment)

    return {
        "sentiment_prob": sentiment_prob,
        "keywords": keywords,
        "keywords_str": ", ".join(keywords) # Helper for display
    }

def analyze_comments(df):
    """
    Wrapper for DataFrame processing to maintain compatibility with existing flow,
    though main.py will likely switch to row-by-row.
    """
    if df.empty or 'Comments' not in df.columns:
        return df

    results = df['Comments'].apply(analyze_comment)
    
    # Expand dictionary results into columns
    df['Sentiment Score'] = results.apply(lambda x: x['sentiment_prob'])
    df['Keywords'] = results.apply(lambda x: x['keywords_str'])
    
    return df
