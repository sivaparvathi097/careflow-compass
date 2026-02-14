import random
import sys
import pandas as pd

SYMPTOMS = ["chest pain","fever","breathlessness","dizziness"]
CONDS = ["hypertension","diabetes","asthma"]


def one():
    age = random.randint(18, 90)
    sys = random.randint(100, 190)
    dia = random.randint(60, 110)
    hr = random.randint(60, 140)
    temp = round(random.uniform(36, 40), 1)

    symptoms = random.sample(SYMPTOMS, random.randint(0, 2))
    conds = random.sample(CONDS, random.randint(0, 2))

    # stronger label logic (learnable patterns)
    # CLEAN learnable rules — model can see these signals
    if sys > 170:
        risk = 2
    elif hr > 120:
        risk = 2
    elif temp > 38.5:
        risk = 1
    elif hr > 100:
        risk = 1
    else:
        risk = 0


    # ✅ RETURN MUST BE INSIDE FUNCTION
    return [
        age,
        sys,
        dia,
        hr,
        temp,
        "|".join(symptoms),
        "|".join(conds),
        risk
    ]


rows = [one() for _ in range(15000)]

df = pd.DataFrame(rows, columns=[
    "age","sys","dia","hr","temp","symptoms","conds","risk"
])

df.to_csv("train.csv", index=False)

print("✅ train.csv generated")
