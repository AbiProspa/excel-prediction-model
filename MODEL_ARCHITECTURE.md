# Prediction Model Architecture (Updated)

## System Overview

The prediction model is a **Hybrid Adaptive AI** pipeline that transforms customer feedback into actionable business insights using Deep Learning (BERT), Bayesian Statistics with Adaptive Weights, and a Feedback Loop for continuous improvement.

```
Excel Input → BERT NLP → Adaptive Bayesian Model → Risk Scoring → Recommendations → Excel Output
      ^                                                                      |
      |__________________________Feedback Loop_______________________________|
```

## Data Flow Architecture

### Input Data Structure
**Source**: `Feedback_Dashboard_Template.xlsm` → `Feedback_Data` sheet

| Column | Type | Purpose |
|--------|------|---------|
| Feedback Type | Text | Category (ATM, POS, Mobile App, etc.) |
| Rating (1–5) | Numeric | Customer satisfaction score |
| Comments | Text | Free-form customer feedback |

### Output Data Structure
**Destination**: Same Excel file → `Output` sheet

| Column | Description |
|--------|-------------|
| Feedback Type | Original category |
| Average Rating | Mean rating per category |
| Average Sentiment Score | **Probability of Negativity** (0.0 = Positive, 1.0 = Negative) |
| Probability Score | Combined Issue Probability (0 to 1) |
| Risk Level | Critical/Warning/Stable classification |
| Top Issue Summary | Key keywords identified |
| Recommendation | Actionable business advice |

## 🔧 Core Components

### 1. Data Loading Engine
- **Purpose**: Safely extract feedback data from Excel using `pandas` and `xlwings`.
- **Features**: Error handling for missing files or empty sheets.

### 2. NLP Analysis Engine (`nlp_engine.py`)

#### Deep Learning Model (BERT)
Uses **DistilBERT** (via `bert_sentiment.py`) for advanced sentiment understanding.
- **Input**: Raw text comment
- **Output**: **Negative Probability** (0.0 to 1.0)
    - 0.0 - 0.3: Positive/Neutral
    - 0.7 - 1.0: Highly Negative
- **Advantage**: Understands context, sarcasm, and nuance better than simple keyword matching.

#### Keyword Extraction
Extracts specific trigger words (e.g., "network", "timeout", "refund") to identify the root cause of issues.

### 3. Bayesian Probability Model (`bayesian_model.py`)

#### Adaptive Weights
Unlike static models, this engine uses **Adaptive Weights** that can be tuned over time.
```python
Issue_Prob = (W_rating * Rating_Prob) + (W_sentiment * Sentiment_Prob)
```
- **Rating Prob**: Normalized (5★ → 0.0, 1★ → 1.0)
- **Sentiment Prob**: Direct output from BERT (0.0 → 1.0)
- **Weights**: Loaded from `weights.json`, allowing the model's sensitivity to rating vs. text to be adjusted.

### 4. Risk Assessment Engine (`risk_engine.py`)

#### Dual-Threshold Logic
Classifies risk logic based on both structural (Rating) and unstructured (Text) signals:

| Risk Level | Logic | Meaning |
|------------|-------|---------|
| **Critical** | Rating ≤ 2.5 **OR** (Rating ≤ 3.5 & NegProb > 0.8) | Severe failure or mismatch between rating and comment. |
| **Warning** | Rating < 4.0 **OR** NegProb > 0.4 | Suboptimal performance or underlying complaints. |
| **Stable** | Rating ≥ 4.0 **AND** NegProb ≤ 0.4 | Healthy system state. |

### 5. Recommendation Engine
Generates specific, actionable advice based on the calculated Risk Level and Feedback Type.

### 6. Feedback Loop & Learning (`feedback_loop.py`)
- **Action**: Logs every prediction, rating, and outcome to `history.csv`.
- **Purpose**: Enables future retraining of weights. If the model flags "Critical" but the issue was minor, the weights can be adjusted based on this history.

## Execution Pipeline

1.  **Load**: Read `Feedback_Data`.
2.  **Analyze (BERT)**: Compute text negativity probability.
3.  **calculate**: Apply Adaptive Bayesian weights.
4.  **Assess**: Determine Risk Level (Critical/Warning/Stable).
5.  **Recommend**: Generate business advice.
6.  **Log**: Save input/output to `history.csv` for learning.
7.  **Export**: Write results to `Output` sheet in Excel.

## Summary of Improvements (vs Legacy)

| Feature | Legacy System | **Current System** |
|---------|---------------|--------------------|
| **NLP** | TextBlob (Simple Polarity) | **DistilBERT (Deep Learning)** |
| **Weights** | Fixed (50/50) | **Adaptive (Loadable)** |
| **Learning** | None | **Feedback Loop (History Log)** |
| **Risk Logic**| Static Thresholds | **Context-Aware Thresholds** |