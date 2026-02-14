import joblib
from pathlib import Path

from .ml_assets.feature_builder import build_features

LABEL_MAP = {0: "Low", 1: "Medium", 2: "High"}

MODEL_PATH = Path(__file__).parent / "ml_assets" / "model.pkl"
model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None


# -----------------------------
# fallback if model missing
# -----------------------------

def fallback_rule(p):
    v = p["vitals"]

    if v["systolic_bp"] > 170:
        return 2, 0.9
    if v["heart_rate"] > 120:
        return 2, 0.85
    if v["temperature"] > 38:
        return 1, 0.7
    return 0, 0.6


# -----------------------------
# MUST match training order
# -----------------------------

MODEL_FEATURE_ORDER = [
    "age","sys","dia","hr","temp",
    "bp_mean","pulse_pressure","shock_index",
    "fever_flag","tachy_flag"
]


# -----------------------------
# Severity-based scoring
# -----------------------------

BASE_SCORE = {
    0: 20,   # Low
    1: 50,   # Medium
    2: 75    # High
}

SPREAD = {
    0: 20,
    1: 25,
    2: 25
}


def compute_severity_score(cid, raw_prob):
    return round(BASE_SCORE[cid] + SPREAD[cid] * raw_prob, 1)


# -----------------------------
# MAIN
# -----------------------------

def predict_risk(patient_json):

    feats = build_features(patient_json)

    if model is not None:
        row = [[feats[k] for k in MODEL_FEATURE_ORDER]]
        probs = model.predict_proba(row)[0]
        cid = int(probs.argmax())
        raw_prob = float(probs.max())
    else:
        cid, raw_prob = fallback_rule(patient_json)

    risk_percent = compute_severity_score(cid, raw_prob)

    top_features = [
        {"feature": k, "value": feats[k], "impact": "high"}
        for k in ["sys","hr","temp"]
    ]

    return {
        "risk_level": LABEL_MAP[cid],
        "risk_score": risk_percent,
        "risk_class_id": cid,
        "top_contributing_features": top_features
    }
