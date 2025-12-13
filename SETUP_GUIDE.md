# Real-Time Excel Dashboard Setup Guide

## 📁 Where to Place Your Dashboard File

### Option 1: Use the Default Location (Recommended)
Place your Excel dashboard file here:
```
prediction_model/data/feedback.xlsx
```
- Replace the existing `feedback.xlsx` with your real data
- Keep the sheet name as `FeedbackData`

### Option 2: Use a Custom Location
Place your dashboard anywhere and specify the path when running:
```bash
python prediction_model/main.py "C:\path\to\your\dashboard.xlsx"
```

## 📊 Excel File Requirements

Your Excel file must have a sheet named **FeedbackData** with these columns:
- `Date` - Date of feedback (e.g., 2023-10-01)
- `Product` - Product name (e.g., ATM, POS, Mobile App)
- `Feedback Type` - Type of feedback (e.g., Availability, Transaction Success)
- `Rating` - Numeric rating (1-5)
- `Comment` - Text feedback
- `Status` - Status (e.g., Open, Closed)

Results will be written to a sheet named **ModelOutput** in the same file.

## 🚀 How to Run

### One-Time Analysis
```bash
python prediction_model/main.py
```

Or with custom file:
```bash
python prediction_model/main.py "C:\Users\YourName\Documents\dashboard.xlsx"
```

### Real-Time Monitoring (Auto-updates on file save)

**Option A: Using batch file**
```bash
run_realtime.bat
```

**Option B: Command line (default file)**
```bash
python prediction_model/realtime_monitor.py
```

**Option C: Command line (custom file)**
```bash
python prediction_model/realtime_monitor.py "C:\path\to\your\dashboard.xlsx"
```

## 🔄 Real-Time Mode Features

- Automatically detects when you save changes to Excel
- Runs the model and updates results within seconds
- Shows timestamp of each update
- Press Ctrl+C to stop monitoring

## 💡 Workflow Example

1. Open your Excel dashboard (`prediction_model/data/feedback.xlsx`)
2. Run `run_realtime.bat` in a separate window
3. Add/edit feedback data in the `FeedbackData` sheet
4. Save the file (Ctrl+S)
5. Wait 2-3 seconds - results automatically appear in `ModelOutput` sheet
6. Refresh Excel to see updated results

## 📦 First-Time Setup

Install dependencies:
```bash
python -m pip install -r prediction_model/requirements.txt
```
