import pandas as pd
from sklearn.linear_model import LogisticRegression
from joblib import dump, load
import os

MODEL_FILE = "models/maker_taker_model.pkl"

def train_maker_taker_model():
    df = pd.read_csv("data/maker_taker_data.csv", header=None)
    df.columns = ["usd_amount", "spread", "depth", "is_taker"]

    X = df[["usd_amount", "spread", "depth"]]
    y = df["is_taker"]

    model = LogisticRegression()
    model.fit(X, y)

    os.makedirs("models", exist_ok=True)
    dump(model, MODEL_FILE)
    print("[✓] Maker/Taker model trained and saved.")

def load_maker_taker_model():
    return load(MODEL_FILE)

def predict_maker_taker_proba(model, usd_amount, spread, depth):
    X = [[usd_amount, spread, depth]]
    proba = model.predict_proba(X)[0]
    return {"maker": proba[0], "taker": proba[1]}
