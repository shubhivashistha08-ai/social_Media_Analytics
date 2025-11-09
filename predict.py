# app/predict.py
from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI(title="Bulk Discount Predictor")

model = joblib.load("app/model.pkl")

@app.get("/")
def home():
    return {"message": "Bulk Discount Predictor API"}

@app.post("/predict")
def predict(unit_price: float, quantity: int, is_pro_customer: int):
    X = pd.DataFrame([[unit_price, quantity, is_pro_customer]],
                     columns=['unit_price', 'quantity', 'is_pro_customer'])
    prediction = model.predict(X)[0]
    return {"bulk_discount_applied": int(prediction)}
