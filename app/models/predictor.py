"""Loads the trained AgeWell risk model and exposes a simple predict API."""
import joblib

from config.config import MODEL_PATH

_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict_risk(age: int, heart_rate: int, systolic_bp: int, cholesterol: int) -> int:
    """Return 1 for High Risk, 0 for Low Risk."""
    model = get_model()
    return int(model.predict([[age, heart_rate, systolic_bp, cholesterol]])[0])
