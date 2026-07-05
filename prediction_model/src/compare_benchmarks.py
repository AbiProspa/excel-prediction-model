import argparse
import os
import sys

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from probability_calibration import calibrate_scores


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.csv")
DEFAULT_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "benchmark_comparison.csv")


def _make_encoder():
    """Keep compatibility with older and newer scikit-learn versions."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def load_history_dataset(path):
    df = pd.read_csv(path)

    required = ["feedback_type", "rating", "sentiment_prob", "final_prob", "outcome"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s) in history file: {missing}")

    for col in ["rating", "sentiment_prob", "final_prob", "outcome"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["rating", "sentiment_prob", "final_prob", "outcome"]).copy()
    df["outcome"] = (df["outcome"] >= 0.5).astype(int)
    df["feedback_type"] = df["feedback_type"].fillna("Unknown").astype(str)

    if df.empty:
        raise ValueError("No valid rows found after cleaning history.csv.")
    if df["outcome"].nunique() < 2:
        raise ValueError("Need both 0 and 1 outcomes to compare classifiers.")

    return df


def split_dataset(df, test_size=0.3, random_state=42):
    stratify = df["outcome"] if df["outcome"].value_counts().min() >= 2 else None
    return train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify,
    )


def build_classical_pipeline(model):
    numeric_features = ["rating", "sentiment_prob"]
    categorical_features = ["feedback_type"]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                numeric_features,
            ),
            (
                "cat",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", _make_encoder()),
                ]),
                categorical_features,
            ),
        ]
    )

    return Pipeline([
        ("preprocess", preprocessor),
        ("model", model),
    ])


def _probabilities_from_estimator(estimator, x_test):
    if hasattr(estimator, "predict_proba"):
        return estimator.predict_proba(x_test)[:, 1]
    return estimator.decision_function(x_test)


def calculate_metrics(model_name, y_true, y_prob, threshold=0.5):
    y_prob = np.clip(np.asarray(y_prob, dtype=float), 0.0, 1.0)
    y_pred = (y_prob >= threshold).astype(int)

    # RIC is not a standard sklearn metric. Here it means Risk Identification
    # Correctness: balanced accuracy across risk and non-risk classes.
    ric = balanced_accuracy_score(y_true, y_pred)

    return {
        "Model": model_name,
        "MAE": mean_absolute_error(y_true, y_prob),
        "MSE": mean_squared_error(y_true, y_prob),
        "RIC": ric,
        "R-square": r2_score(y_true, y_prob),
        "Precision": precision_score(y_true, y_pred, zero_division=0),
        "Accuracy": accuracy_score(y_true, y_pred),
        "Recall": recall_score(y_true, y_pred, zero_division=0),
        "F1-score": f1_score(y_true, y_pred, zero_division=0),
    }


def calibrate_bayesian_probabilities(train_df, test_df):
    """
    Calibrate the Bayesian-BERT probability scale using only the training split.

    The core model remains the Bayesian score from history.csv. Calibration fixes
    systematic over/under-confidence so regression-style metrics (MAE/MSE/R2)
    are compared on a fair probability scale instead of raw, uncalibrated scores.
    """
    return calibrate_scores(test_df["final_prob"], train_df, min_rows=10)


def compare_models(history_path=DEFAULT_HISTORY_FILE, output_path=DEFAULT_OUTPUT_FILE):
    df = load_history_dataset(history_path)
    train_df, test_df = split_dataset(df)

    x_train = train_df[["rating", "sentiment_prob", "feedback_type"]]
    y_train = train_df["outcome"]
    x_test = test_df[["rating", "sentiment_prob", "feedback_type"]]
    y_test = test_df["outcome"]

    rows = []

    logistic = build_classical_pipeline(
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    )
    logistic.fit(x_train, y_train)
    rows.append(calculate_metrics(
        "Logistic Regression",
        y_test,
        _probabilities_from_estimator(logistic, x_test),
    ))

    forest = build_classical_pipeline(
        RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
        )
    )
    forest.fit(x_train, y_train)
    rows.append(calculate_metrics(
        "Random Forest",
        y_test,
        _probabilities_from_estimator(forest, x_test),
    ))

    rows.append(calculate_metrics(
        "Standard BERT",
        y_test,
        test_df["sentiment_prob"],
    ))

    calibrated_bayesian_prob = calibrate_bayesian_probabilities(train_df, test_df)
    rows.append(calculate_metrics(
        "Bayesian-BERT",
        y_test,
        calibrated_bayesian_prob,
    ))

    comparison = pd.DataFrame(rows)
    metric_cols = [col for col in comparison.columns if col != "Model"]
    comparison[metric_cols] = comparison[metric_cols].round(4)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    comparison.to_csv(output_path, index=False)
    return comparison, output_path, len(train_df), len(test_df)


def main():
    parser = argparse.ArgumentParser(
        description="Compare Bayesian-BERT against benchmark models."
    )
    parser.add_argument("--history", default=DEFAULT_HISTORY_FILE)
    parser.add_argument("--output", default=DEFAULT_OUTPUT_FILE)
    args = parser.parse_args()

    try:
        comparison, output_path, train_count, test_count = compare_models(
            args.history,
            args.output,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Training rows: {train_count}")
    print(f"Test rows:     {test_count}")
    print("\n--- BENCHMARK COMPARISON ---")
    print(comparison.to_string(index=False))
    print(f"\nSaved comparison to: {output_path}")
    print(
        "\nNote: RIC is implemented here as balanced accuracy "
        "(Risk Identification Correctness)."
    )


if __name__ == "__main__":
    main()
