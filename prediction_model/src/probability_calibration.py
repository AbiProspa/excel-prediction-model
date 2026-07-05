import os

import pandas as pd
from sklearn.isotonic import IsotonicRegression


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.csv")
MIN_CALIBRATION_ROWS = 20


def _clean_training_frame(df):
    required = ["final_prob", "outcome"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        return pd.DataFrame(columns=required)

    clean = df[required].copy()
    clean["final_prob"] = pd.to_numeric(clean["final_prob"], errors="coerce")
    clean["outcome"] = pd.to_numeric(clean["outcome"], errors="coerce")
    clean = clean.dropna(subset=required)
    clean["final_prob"] = clean["final_prob"].clip(0, 1)
    clean["outcome"] = (clean["outcome"] >= 0.5).astype(int)
    return clean


def fit_isotonic_calibrator(training_df, min_rows=MIN_CALIBRATION_ROWS):
    """
    Fit a monotonic probability calibrator from resolved historical outcomes.

    Returns None when there is not enough resolved history or when the history
    has only one outcome class. In that case callers should keep raw scores.
    """
    clean = _clean_training_frame(training_df)
    if len(clean) < min_rows:
        return None
    if clean["final_prob"].nunique() < 2 or clean["outcome"].nunique() < 2:
        return None

    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(clean["final_prob"], clean["outcome"])
    return calibrator


def calibrate_scores(raw_scores, training_df, min_rows=MIN_CALIBRATION_ROWS):
    calibrator = fit_isotonic_calibrator(training_df, min_rows=min_rows)
    scores = pd.Series(raw_scores, dtype=float).clip(0, 1)
    if calibrator is None:
        return scores
    return pd.Series(calibrator.predict(scores), index=scores.index).clip(0, 1)


def calibrate_scores_from_history(raw_scores, history_path=DEFAULT_HISTORY_FILE):
    if not os.path.exists(history_path):
        return pd.Series(raw_scores, dtype=float).clip(0, 1)

    try:
        history_df = pd.read_csv(history_path)
    except Exception as exc:
        print(f"[WARNING] Could not load calibration history: {exc}")
        return pd.Series(raw_scores, dtype=float).clip(0, 1)

    return calibrate_scores(raw_scores, history_df)
