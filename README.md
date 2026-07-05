# Prediction Model — Hybrid Adaptive AI

A feedback-risk analysis pipeline wired into Excel. It reads customer feedback,
scores operational risk per product using **DistilBERT** sentiment + an
**adaptive Bayesian** model, writes recommendations back into the workbook, and
logs every prediction so it can measure its own accuracy over time.

See [MODEL_ARCHITECTURE.md](MODEL_ARCHITECTURE.md) and
[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for the deep dive.

## Setup

```bash
pip install -r prediction_model/requirements.txt
```

## Pipeline

```
Excel (Feedback_Data) → BERT NLP → Adaptive Bayesian → Risk → Recommend → Log → Excel (Output + Dashboard)
        ↑___________________________ Feedback Loop (history.csv → weights) ___________________________|
```

| Stage | Module |
|-------|--------|
| Load (xlwings, fuzzy headers, filters to 5 core services) | `src/load_data.py` |
| NLP — DistilBERT negative-probability + keyword extraction (falls back to TextBlob, then keywords) | `src/nlp_engine.py`, `src/bert_sentiment.py` |
| Adaptive Bayesian probability + keyword priors + probability calibration | `src/bayesian_model.py`, `src/probability_calibration.py` |
| Risk scoring (Critical / Warning / Stable) | `src/risk_engine.py` |
| Recommendations per (product × risk) | `src/recommendation_engine.py` |
| History logging | `src/feedback_loop.py` |
| Excel export + Dashboard update | `src/export_results.py`, `main.py` |
| Benchmark comparison (Logistic Regression / Random Forest / Standard BERT / Bayesian-BERT) | `src/compare_benchmarks.py` |
| Evaluation (MAE / MSE / R² / BIC) | `src/evaluate_model.py` |

The five **core services** (canonical product names used end to end):
`ATM`, `App`, `Online Banking`, `Service`, `Loan Process`.

## Running

```bash
# Full pipeline (reads/writes prediction_model/data/Feedback_Dashboard_Template.xlsm)
python prediction_model/main.py

# Auto-rerun whenever the workbook is saved
python prediction_model/realtime_monitor.py

# Performance metrics on history.csv
python prediction_model/src/evaluate_model.py --history

# Compare Bayesian-BERT against baseline models
python prediction_model/src/compare_benchmarks.py
```

`main.py` is also Excel-callable via the `xlwings` add-in
(`run_model_from_excel`, `run_evaluation_from_excel`).

## Testing

A non-Excel integration test exercises the full logic pipeline (NLP → Bayesian →
Risk → Recommend) plus evaluation — no Excel/network required:

```bash
python prediction_model/tests/test_pipeline.py
```

Test data helpers (these drive Excel, so they need Excel installed):

```bash
python prediction_model/scripts/populate_history.py            # reset baseline history
python prediction_model/scripts/generate_scenarios.py --scenario outage|stable|mixed
```

## Note on evaluation metrics

In a demo there is **no real ground truth**. When you run the model, predictions
are logged to `history.csv` as `Pending`. Evaluation then fills those in with a
*simulated, seeded* outcome (a biased coin flip on the predicted probability) so
the metrics are non-trivial yet honest — they reflect genuine 0/1-vs-probability
error rather than grading the model against its own threshold. Replace these with
real, user-confirmed outcomes for a true evaluation.

## Benchmark comparison

`compare_benchmarks.py` evaluates Bayesian-BERT against Logistic Regression,
Random Forest, and Standard BERT on the same train/test split from
`history.csv`. Classical baselines are trained on the training split. The
Bayesian-BERT row uses the existing hybrid probability score, then applies an
isotonic calibration map learned from the training split only. The live Excel
model now uses the same calibration approach when enough resolved history
exists, while safely falling back to the raw Bayesian-BERT score when history is
not sufficient. This keeps the benchmark honest while correcting raw probability
overconfidence, so MAE, MSE, and R-square reflect a calibrated risk probability
rather than an uncalibrated score.
