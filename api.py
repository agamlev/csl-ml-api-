from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd

app = FastAPI(title="CSL Won Probability API")

with open("csl_model.pkl", "rb") as f:
    bundle = pickle.load(f)

model = bundle["model"]
plan_encoder = bundle["plan_encoder"]
features = bundle["features"]


class Customer(BaseModel):
    customer_health_score: int
    customer_plan: str  # Basic / Pro / Premium / Enterprise
    usage_volume: int
    restricted_feature_attempt: int
    feature_related_inquiry: int
    csat_score: float


@app.get("/")
def root():
    return {"status": "ok", "message": "CSL Won Probability API is running"}


@app.post("/predict")
def predict(customer: Customer):
    plan_enc = plan_encoder.transform([customer.customer_plan])[0]
    row = pd.DataFrame([[
        customer.customer_health_score,
        plan_enc,
        customer.usage_volume,
        customer.restricted_feature_attempt,
        customer.feature_related_inquiry,
        customer.csat_score,
    ]], columns=features)
    prob = round(model.predict_proba(row)[0][1] * 100, 1)
    return {
        "won_probability_%": prob,
        "verdict": "likely won" if prob >= 60 else "at risk",
    }
