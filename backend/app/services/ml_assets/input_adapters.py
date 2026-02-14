import pandas as pd
import json

def from_csv(path):
    df = pd.read_csv(path)
    records = []
    for _, r in df.iterrows():
        records.append({
            "demographics": {"age": r.age, "gender": r.gender},
            "symptoms": r.symptoms.split("|"),
            "vitals": {
                "systolic_bp": r.sys,
                "diastolic_bp": r.dia,
                "heart_rate": r.hr,
                "temperature": r.temp
            },
            "pre_existing_conditions": r.conditions.split("|")
        })
    return records


def from_json(path):
    with open(path) as f:
        return json.load(f)
