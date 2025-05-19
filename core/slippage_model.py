import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

MODEL_PATH = "models/slippage_model.pkl"

def train_model():
    df = pd.read_csv("data/slippage_data.csv", header=None)
    df.columns = ['usd_amount', 'best_ask', 'avg_price', 'slippage']
    X = df[['usd_amount', 'best_ask']]
    y = df['slippage']

    model = LinearRegression()
    model.fit(X, y)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print("[✓] Model trained and saved.")

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model file not found. Train the model first.")
    return joblib.load(MODEL_PATH)

def predict_slippage(model, usd_amount, best_ask):
    return model.predict([[usd_amount, best_ask]])[0]
