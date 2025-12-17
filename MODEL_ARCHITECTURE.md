# Prediction Model Architecture & How It Works

## System Overview

The prediction model is a **6-stage pipeline** that transforms customer feedback into actionable business insights using NLP, Bayesian statistics, and risk assessment algorithms.

```
Excel Input → NLP Analysis → Bayesian Model → Risk Scoring → Recommendations → Excel Output
```

##  Data Flow Architecture

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
| Average Sentiment Score | NLP-derived sentiment (-1 to +1) |
| Probability Score | Bayesian risk probability (0 to 1) |
| Risk Level | Critical/Warning/Stable classification |
| Top Issue Summary | Key problems identified |
| Recommendation | Actionable business advice |

## 🔧 Core Components

### 1. Data Loading Engine (`load_data.py`)
```python
# Reads Excel using pandas with error handling
df = pd.read_excel(excel_path, sheet_name=sheet_name)
```
- **Purpose**: Safely extract feedback data from Excel
- **Error Handling**: Missing files, empty sheets, column validation
- **Output**: Clean pandas DataFrame

### 2. NLP Analysis Engine (`nlp_engine.py`)

#### Sentiment Analysis
Uses **TextBlob** library for polarity scoring:
```python
sentiment_score = TextBlob(comment).sentiment.polarity
# Returns: -1 (very negative) to +1 (very positive)
```

#### Keyword Extraction
Pattern matching against predefined banking issue triggers:
```python
trigger_words = ["network down", "failed", "slow", "crash", "timeout", "rude", "wait"]
```
- **Algorithm**: Simple string matching in lowercase text
- **Output**: Comma-separated list of detected issues

### 3. Bayesian Probability Model (`bayesian_model.py`)

#### Mathematical Foundation
Converts ratings and sentiment into issue probability using inverse relationships:

**Rating Probability**:
```
P(issue|rating) = (5 - rating) / 4
```
- Rating 1 → Probability 1.0 (100% chance of issue)
- Rating 5 → Probability 0.0 (0% chance of issue)

**Sentiment Probability**:
```
P(issue|sentiment) = (1 - sentiment) / 2
```
- Sentiment -1 → Probability 1.0 (very negative = high issue probability)
- Sentiment +1 → Probability 0.0 (very positive = low issue probability)

**Combined Score**:
```
Final Probability = (Rating Prob + Sentiment Prob) / 2
```

#### Aggregation Logic
Groups feedback by type and calculates:
- Mean rating per category
- Mean sentiment per category
- Combined probability score per category

### 4. Risk Assessment Engine (`risk_engine.py`)

#### Risk Classification Algorithm
Uses **dual-threshold logic** combining rating and sentiment:

```python
def classify_risk(avg_rating, avg_sentiment):
    if avg_rating <= 2 and avg_sentiment < -0.3:
        return "Critical"
    elif (2 < avg_rating < 3.5) or (-0.3 <= avg_sentiment < 0):
        return "Warning"
    elif avg_rating >= 4 and avg_sentiment >= 0:
        return "Stable"
    else:
        return fallback_logic(avg_rating)
```

#### Risk Thresholds
| Risk Level | Rating Condition | Sentiment Condition |
|------------|------------------|---------------------|
| **Critical** | ≤ 2.0 | < -0.3 (strongly negative) |
| **Warning** | 2.0 - 3.5 | -0.3 to 0.0 (mildly negative) |
| **Stable** | ≥ 4.0 | ≥ 0.0 (neutral/positive) |

### 5. Recommendation Engine (`recommendation_engine.py`)

#### Business Logic Matrix
Generates specific recommendations based on **Feedback Type × Risk Level**:

```python
recommendations = {
    "ATM": {
        "Critical": "Immediate maintenance required for ATM network...",
        "Warning": "Increase ATM cash replenishment frequency...",
        "Stable": "ATM network operating normally..."
    },
    # ... other categories
}
```

#### Top Issue Extraction
Analyzes keyword frequency to identify primary concerns:
```python
def extract_top_issues(keywords):
    # Count keyword frequency
    # Return top 3 most mentioned issues
```

### 6. Excel Export Engine (`export_results.py`)
- **Technology**: xlwings for live Excel integration
- **Features**: Overwrites existing data, preserves formatting
- **Real-time**: Can be triggered from Excel macros

## Algorithm Details

### Bayesian Inference Logic
The model applies **naive Bayes principles** assuming:
1. **Independence**: Rating and sentiment are independent predictors
2. **Prior Knowledge**: Banking domain expertise encoded in thresholds
3. **Posterior Calculation**: Combined probability represents likelihood of requiring intervention

### Statistical Aggregation
For each feedback category:
```python
# Group by feedback type
grouped_data = df.groupby('Feedback Type').agg({
    'Rating': 'mean',
    'Sentiment Score': 'mean',
    'Keywords': lambda x: ' '.join(x)
})
```

### Risk Scoring Mathematics
Uses **weighted scoring** for edge cases:
```python
if rating <= 2.5:
    risk = "Critical"
elif rating < 3.75:
    risk = "Warning"
else:
    risk = "Stable"
```

## Execution Pipeline

### Sequential Processing
1. **Load** → Validate Excel data structure
2. **Analyze** → Extract sentiment + keywords from comments
3. **Calculate** → Apply Bayesian probability formulas
4. **Assess** → Classify risk levels using thresholds
5. **Recommend** → Generate business-specific advice
6. **Export** → Write results back to Excel

### Error Handling Strategy
- **Missing Data**: Default values (rating=5, sentiment=0)
- **Invalid Excel**: Graceful failure with error messages
- **Empty Comments**: Skip NLP analysis, use rating only
- **Unknown Categories**: Apply generic recommendations

## Model Performance Characteristics

### Strengths
- **Real-time Processing**: Handles 1000+ records in seconds
- **Business-Focused**: Outputs directly actionable recommendations
- **Excel Integration**: Seamless workflow for business users
- **Interpretable**: Clear mathematical relationships

### Limitations
- **Simple NLP**: Basic keyword matching (not deep learning)
- **Static Thresholds**: Risk levels use fixed cutoffs
- **No Learning**: Model doesn't adapt from historical performance
- **English Only**: TextBlob optimized for English text

## Business Value Proposition

### Automated Insights
Converts raw feedback into prioritized action items:
- **Critical Issues**: Immediate escalation required
- **Warning Trends**: Proactive intervention opportunities  
- **Stable Areas**: Confirmation of effective processes

### Scalability
Processes large volumes of feedback without manual analysis:
- **Time Savings**: Minutes instead of hours for analysis
- **Consistency**: Standardized risk assessment criteria
- **Audit Trail**: Mathematical basis for all decisions

## Technical Integration

### Excel Connectivity
```python
@xw.sub
def run_model_from_excel():
    # Can be triggered directly from Excel VBA
    wb = xw.Book.caller()
    run_model(wb.fullname)
```

### Command Line Interface
```bash
python main.py --excel-path "custom_file.xlsx"
```

### Real-time Monitoring
```bash
# Watches for Excel file changes and auto-runs model
python realtime_monitor.py
```

This architecture provides a robust, scalable solution for transforming customer feedback into actionable business intelligence while maintaining simplicity and interpretability for business stakeholders.