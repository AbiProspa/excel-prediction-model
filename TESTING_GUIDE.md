# 📊 AI Prediction Model - Testing & Verification Guide

This guide provides step-by-step instructions on how to test the system with diverse data and verify that your performance metrics (**MAE, MSE**) are updating correctly.

---

## 🧪 Phase 1: Testing Model Logic (Changing Outputs)

If your dashboard figures are stay the same, it is because the input data is not changing. Use these scripts to inject different "real-world" scenarios:

### 1. Run a 'Risk' Scenario
This simulates a major system outage (low ratings, keywords like "crash").
```powershell
python prediction_model/scripts/generate_scenarios.py --scenario outage
```
**Expected Result**: Open Excel. You should see "Critical" risk levels for ATM and Online Banking.

### 2. Run a 'Stable' Scenario
This simulates a period of high performance (high ratings, positive buzz).
```powershell
python prediction_model/scripts/generate_scenarios.py --scenario stable
```
**Expected Result**: Open Excel. All products should shift to "Stable" status.

### 3. Run a 'Mixed' Scenario (Default)
A realistic blend of feedback.
```powershell
python prediction_model/scripts/generate_scenarios.py --scenario mixed
```

---

## 📈 Phase 2: Testing Performance Metrics (Changing MAE/MSE)

The **MAE (Mean Absolute Error)** and **MSE (Mean Squared Error)** represent how accurately your model is predicting real-world outcomes. 

> [!IMPORTANT]
> Metrics only update when the model knows the **Ground Truth** (the outcome). 
> When you run the model, it logs predictions as **"Pending"** in `history.csv`.
> Pending records are *excluded* from calculations to prevent unverified data from skewing metrics.

### 1. Inject some history
Reset your baseline history if needed (Warning: overwrite):
```powershell
python prediction_model/scripts/populate_history.py
```

### 2. Run the Model (Creates "Pending" records)
Inject any scenario from Phase 1, then run the orchestrator:
```powershell
python prediction_model/main.py
```

### 3. Verify Static Metrics
Run evaluation. Notice the figures stay the same because the new records from Step 2 are still "Pending".
```powershell
python prediction_model/src/evaluate_model.py --history
```

### 4. Resolve the Pending Outcomes
This "teaches" the model what actually happened (simulating a manager's confirmation). This will finally update your metrics:
```powershell
python prediction_model/scripts/resolve_pending.py
```

### 5. Verify Changing Metrics
Run evaluation again. You will see **MAE, MSE, and R2** shift to reflect the new performance data!
```powershell
python prediction_model/src/evaluate_model.py --history
```

---

## 🧰 Summary of Indicators

- **Lower MAE/MSE**: The model is becoming more accurate.
- **Higher R2 (closer to 1.0)**: The model's predictions strongly correlate with actual outcomes.
- **Reason for Static Figures**: If no new *resolved* (non-pending) data is added to `history.csv`, the math is run on the same dataset every time, yielding identical results.
