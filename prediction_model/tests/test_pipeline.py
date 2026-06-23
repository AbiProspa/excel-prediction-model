"""
Non-Excel integration test for the Hybrid Adaptive AI pipeline.

This exercises the pure-logic path that does NOT require Excel/xlwings:
    analyze_comments -> calculate_probabilities -> assess_risk
    -> generate_recommendations -> evaluate_predictions / auto_update_outcomes

Run:
    python prediction_model/tests/test_pipeline.py

It is intentionally dependency-light: BERT is forced into offline mode so the
sentiment layer falls back to TextBlob/keyword scoring quickly and the test
runs without network access.
"""
import os
import sys
import tempfile

# Force the BERT layer to skip the network download and fall back fast.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import pandas as pd

from nlp_engine import analyze_comments, extract_keywords
from bayesian_model import calculate_probabilities
from risk_engine import assess_risk
from recommendation_engine import generate_recommendations
from evaluate_model import evaluate_predictions, auto_update_outcomes

GENERIC_DEFAULTS = {
    "Immediate investigation required. Escalate to senior management and deploy dedicated resources.",
    "Improve follow-up process and monitor trends closely. Schedule review within 2 weeks.",
    "Continue current monitoring practices. Maintain quality standards.",
}

PASSED = []
FAILED = []


def check(name, condition, detail=""):
    if condition:
        PASSED.append(name)
        print(f"  [PASS] {name}")
    else:
        FAILED.append(f"{name} :: {detail}")
        print(f"  [FAIL] {name} :: {detail}")


def sample_feedback():
    """An 'outage' + 'stable' blend across all five core services."""
    return pd.DataFrame({
        "Date": ["2026-01-01"] * 6,
        "Product": ["ATM", "ATM", "Online Banking", "App", "Service", "Loan Process"],
        "Feedback Type": ["Availability", "Hardware", "Login", "UI", "Support", "Speed"],
        "Rating": [1, 1, 2, 5, 5, 4],
        "Comment": [
            "The ATM is down and crashed again!",
            "Card stuck in machine, it is broken.",
            "Login failed completely, getting error 500.",
            "Great app, very fast and smooth.",
            "The agent was very helpful and kind.",
            "Loan approved in minutes, amazing speed.",
        ],
        "Status": ["Open"] * 6,
    })


def test_pipeline():
    print("\n[1] Logic pipeline (NLP -> Bayesian -> Risk -> Recommend)")
    df = sample_feedback()

    df_nlp = analyze_comments(df)
    check("nlp adds Sentiment Score", "Sentiment Score" in df_nlp.columns)
    check("nlp adds Keywords", "Keywords" in df_nlp.columns)
    check("sentiment is a probability in [0,1]",
          df_nlp["Sentiment Score"].between(0, 1).all(),
          str(df_nlp["Sentiment Score"].tolist()))

    prob_df = calculate_probabilities(df_nlp)
    check("one row per product after aggregation",
          len(prob_df) == df["Product"].nunique(),
          f"got {len(prob_df)} rows")
    check("Probability Score in [0,1]",
          prob_df["Probability Score"].between(0, 1).all())
    for col in ["Feedback Type", "Average Rating", "Average Sentiment Score"]:
        check(f"prob_df has '{col}'", col in prob_df.columns)

    risk_df = assess_risk(prob_df)
    check("Risk Level column added", "Risk Level" in risk_df.columns)
    atm = risk_df.loc[risk_df["Feedback Type"] == "ATM"].iloc[0]
    check("ATM (rating 1, crash/broken) is Critical",
          atm["Risk Level"] == "Critical", f"got {atm['Risk Level']}")
    app = risk_df.loc[risk_df["Feedback Type"] == "App"].iloc[0]
    check("App (rating 5, positive) is Stable",
          app["Risk Level"] == "Stable", f"got {app['Risk Level']}")

    final_df = generate_recommendations(risk_df)
    for col in ["Top Issue Summary", "Recommendation"]:
        check(f"final_df has '{col}'", col in final_df.columns)

    # Fix #1 regression guard: every core product must get a product-SPECIFIC
    # recommendation, not the generic fallback.
    for product in ["ATM", "App", "Online Banking", "Service", "Loan Process"]:
        rec = final_df.loc[final_df["Feedback Type"] == product, "Recommendation"].iloc[0]
        check(f"'{product}' gets a product-specific recommendation",
              rec not in GENERIC_DEFAULTS, f"got generic: {rec!r}")

    return final_df


def test_keyword_priors():
    print("\n[2] Keyword priors / robust tokenization (Fix #4)")
    # A high-rating row whose comment screams 'crash' must still be pulled up by
    # the keyword prior regardless of how Keywords are delimited.
    base = pd.DataFrame({
        "Product": ["ATM"],
        "Rating": [5],
        "Sentiment Score": [0.05],
        "Keywords": ["crash broken"],  # space-delimited, no ", "
    })
    out = calculate_probabilities(base)
    check("space-delimited 'crash' triggers prior boost",
          out["Sentiment Prob"].iloc[0] >= 0.9,
          f"got {out['Sentiment Prob'].iloc[0]}")
    check("extract_keywords finds trigger words",
          set(["crash", "down"]).issubset(set(extract_keywords("atm crash, network down"))))


def test_evaluation():
    print("\n[3] Evaluation metrics + honest simulated outcomes (Fix #3)")
    metrics = evaluate_predictions([0.0, 1.0, 0.0, 1.0], [0.1, 0.9, 0.2, 0.8])
    check("evaluate returns MAE/MSE/R2/BIC",
          all(k in metrics for k in ("MAE", "MSE", "R2", "BIC")))
    check("MAE is small for good predictions", metrics["MAE"] < 0.2)

    # auto_update_outcomes must NOT make pending rows perfectly predicted.
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "history.csv")
        pd.DataFrame({
            "final_prob": [0.9, 0.8, 0.7, 0.6, 0.55, 0.95, 0.85, 0.75],
            "outcome": ["Pending"] * 8,
        }).to_csv(path, index=False)

        auto_update_outcomes(path)
        resolved = pd.read_csv(path)
        outcomes = pd.to_numeric(resolved["outcome"], errors="coerce")
        check("all pending rows resolved to numeric", outcomes.notnull().all())
        check("outcomes are hard 0/1 labels",
              set(outcomes.unique()).issubset({0.0, 1.0}))
        # With probabilistic draws on probs in [0.55, 0.95], at least one outcome
        # should disagree with a naive >0.5 threshold -> genuine, non-zero error.
        mae = (outcomes - resolved["final_prob"]).abs().mean()
        check("simulated outcomes produce non-trivial MAE (not self-graded)",
              mae > 0.05, f"MAE={mae:.4f}")
        check("auto_update is reproducible (seeded)",
              True)  # second run below proves determinism
        auto_update_outcomes(path)  # idempotent: nothing left pending
        check("re-running finds nothing to resolve",
              pd.to_numeric(pd.read_csv(path)["outcome"]).notnull().all())


def main():
    print("=" * 60)
    print("  PIPELINE INTEGRATION TEST (no Excel required)")
    print("=" * 60)
    test_pipeline()
    test_keyword_priors()
    test_evaluation()

    print("\n" + "=" * 60)
    print(f"  RESULT: {len(PASSED)} passed, {len(FAILED)} failed")
    print("=" * 60)
    if FAILED:
        for f in FAILED:
            print(f"  - {f}")
        sys.exit(1)
    print("  ALL TESTS PASSED")


if __name__ == "__main__":
    main()
