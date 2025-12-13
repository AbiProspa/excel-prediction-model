# Quick Start Guide - Prediction Model

## 🚀 3 Ways to Run This Project

### Method 1: One-Click Run (Easiest)
```bash
# Double-click this file in Windows Explorer:
run_model.bat
```

### Method 2: Command Line
```bash
# 1. Install dependencies
pip install -r prediction_model/requirements.txt

# 2. Generate sample data (if needed)
python generate_data.py

# 3. Run the model
python prediction_model/main.py
```

### Method 3: Real-Time Excel Monitoring
```bash
# Double-click this file for auto-updates:
run_realtime.bat
```

## 📋 Prerequisites
- Python 3.7+ installed
- Excel (for viewing results)

## 📁 What Happens When You Run
1. **Input**: Reads `prediction_model/data/feedback.xlsx` (FeedbackData sheet)
2. **Processing**: 
   - NLP sentiment analysis
   - Bayesian probability calculations
   - Risk scoring
   - Generates recommendations
3. **Output**: Writes results to `ModelOutput` sheet in same Excel file

## 🔧 Troubleshooting
- **No Python?** Install from [python.org](https://python.org)
- **Missing Excel file?** Run `python generate_data.py` first
- **Import errors?** Run `pip install -r prediction_model/requirements.txt`

## 📊 Excel Integration
1. Open `prediction_model/data/feedback.xlsx`
2. View results in `ModelOutput` sheet
3. For real-time updates, use `run_realtime.bat`

## 🎯 Expected Output
- Risk scores (Critical/Warning/Stable)
- Sentiment analysis results
- Product recommendations
- Probability calculations