import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from xgboost import XGBClassifier

df = pd.read_csv("train.csv")

# derived features
df["bp_mean"] = (df.sys + df.dia)/2
df["pulse_pressure"] = df.sys - df.dia
df["shock"] = df.hr / df.sys
df["fever_flag"] = (df.temp>=38).astype(int)
df["tachy_flag"] = (df.hr>100).astype(int)

X = df[[
    "age","sys","dia","hr","temp",
    "bp_mean","pulse_pressure","shock",
    "fever_flag","tachy_flag"
]]

y = df["risk"]

Xtr,Xte,ytr,yte = train_test_split(
    X,y,test_size=0.2,stratify=y,random_state=42
)

model = XGBClassifier(
    n_estimators=600,
    max_depth=6,
    learning_rate=0.07,
    subsample=0.9,
    eval_metric="mlogloss"
)

model.fit(Xtr,ytr)

pred = model.predict(Xte)

print("MACRO F1:", f1_score(yte,pred,average="macro"))

joblib.dump(model, "../app/services/ml_assets/model.pkl")

print("✅ model saved")
