import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"

# Global state for model availability
BERT_AVAILABLE = False
tokenizer = None
model = None

# Attempt to load BERT
print(f"Loading BERT model: {MODEL_NAME}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    BERT_AVAILABLE = True
    print("✓ BERT model loaded successfully.")
except Exception as e:
    print(f"⚠️ WARNING: Could not load BERT model due to network/system issue: {e}")
    print("⚠️ System will fall back to TextBlob/Heuristic mode.")
    BERT_AVAILABLE = False

# Fallback dependencies
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("⚠️ TextBlob also not found. Using simple keyword fallback.")

def get_negative_probability(text: str) -> float:
    """
    Returns the probability (0.0 to 1.0) that the text is NEGATIVE.
    
    Mode 1: DistilBERT (High Precision, requires Model)
    Mode 2: TextBlob (Medium, local fallback)
    Mode 3: Keyword (Low, emergency fallback)
    """
    if not text or not isinstance(text, str):
        return 0.5  # neutral fallback

    # MODE 1: BERT
    if BERT_AVAILABLE:
        try:
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=128
            )
            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.softmax(outputs.logits, dim=1)
            
            # Label 0: NEGATIVE, Label 1: POSITIVE for sst-2
            negative_prob = probs[0][0].item()
            return round(negative_prob, 4)
        except Exception as e:
            logger.error(f"Error during BERT inference: {e}")
            # Fall through to fallback
            
    # MODE 2: TextBlob Fallback
    if TEXTBLOB_AVAILABLE:
        analysis = TextBlob(text)
        # Polarity: -1 (Negative) to +1 (Positive)
        # We need Negative Probability (0 to 1)
        # If polarity is -1, NegProb should be 1.0
        # If polarity is +1, NegProb should be 0.0
        # Formula: (1 - polarity) / 2
        # Example: Polarity -0.5 -> (1 - -0.5)/2 = 0.75 (75% negative)
        neg_prob = (1 - analysis.sentiment.polarity) / 2
        return round(neg_prob, 4)

    # MODE 3: Rudimentary Keyword Fallback
    lower_text = text.lower()
    neg_keywords = ["bad", "terrible", "fail", "slow", "error", "issue", "broken", "worst", "rude"]
    pos_keywords = ["good", "great", "fast", "excellent", "love", "best", "fixed"]
    
    neg_count = sum(1 for w in neg_keywords if w in lower_text)
    pos_count = sum(1 for w in pos_keywords if w in lower_text)
    
    if neg_count > pos_count:
        return 0.8
    elif pos_count > neg_count:
        return 0.2
    
    return 0.5
