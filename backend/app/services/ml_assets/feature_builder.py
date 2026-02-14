from .vocab import SYMPTOMS, CONDITIONS

def build_features(p):
    feats = {}

    v = p["vitals"]
    d = p["demographics"]

    feats["age"] = d["age"]
    feats["sys"] = v["systolic_bp"]
    feats["dia"] = v["diastolic_bp"]
    feats["hr"] = v["heart_rate"]
    feats["temp"] = v["temperature"]

    feats["bp_mean"] = (v["systolic_bp"] + v["diastolic_bp"]) / 2
    feats["pulse_pressure"] = v["systolic_bp"] - v["diastolic_bp"]
    feats["shock_index"] = v["heart_rate"] / max(v["systolic_bp"], 1)

    feats["fever_flag"] = int(v["temperature"] >= 38)
    feats["tachy_flag"] = int(v["heart_rate"] > 100)

    symptoms = set(p["symptoms"])
    for s in SYMPTOMS:
        feats[f"sym_{s.replace(' ','_')}"] = int(s in symptoms)

    conds = set(p["pre_existing_conditions"])
    for c in CONDITIONS:
        feats[f"cond_{c}"] = int(c in conds)

    feats["cond_count"] = len(conds)
    feats["sym_count"] = len(symptoms)

    return feats
