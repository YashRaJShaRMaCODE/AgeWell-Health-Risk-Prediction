"""Flask REST API entry layer for AgeWell (optional alternative to the Streamlit UI)."""
import hmac
import logging
import math

from flask import Flask, jsonify, request

from app.services.health_service import process_patient
from app.utils import db
from config.config import API_AUTH_TOKEN

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
logger = logging.getLogger(__name__)

FIELD_RANGES = {
    "age": (40, 120, True),
    "heart_rate": (30, 200, True),
    "systolic_bp": (80, 250, True),
    "cholesterol": (100, 400, True),
    "weight": (30, 200, False),
    "height": (1, 2.2, False),
}


@app.before_request
def require_api_token():
    if request.endpoint not in {"predict", "records"}:
        return None
    if len(API_AUTH_TOKEN) < 32:
        return jsonify({"error": "API authentication is not configured"}), 503

    scheme, separator, token = request.headers.get("Authorization", "").partition(" ")
    if not separator or scheme.lower() != "bearer" or not token.isascii() or not hmac.compare_digest(token, API_AUTH_TOKEN):
        response = jsonify({"error": "Unauthorized"})
        response.status_code = 401
        response.headers["WWW-Authenticate"] = "Bearer"
        return response
    return None


def parse_patient_payload(payload):
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object")

    missing = [field for field in FIELD_RANGES if field not in payload]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")

    values = {}
    for field, (minimum, maximum, integer) in FIELD_RANGES.items():
        try:
            value = float(payload[field])
        except (TypeError, ValueError):
            raise ValueError(f"{field} must be a number") from None
        if not math.isfinite(value) or not minimum <= value <= maximum:
            raise ValueError(f"{field} must be between {minimum} and {maximum}")
        if integer and not value.is_integer():
            raise ValueError(f"{field} must be a whole number")
        values[field] = int(value) if integer else value

    for field, default in (("save_to_db", False), ("generate_pdf", False)):
        value = payload.get(field, default)
        if not isinstance(value, bool):
            raise ValueError(f"{field} must be a boolean")
        values[field] = value
    return values


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    try:
        values = parse_patient_payload(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        result = process_patient(
            age=values["age"],
            hr=values["heart_rate"],
            bp=values["systolic_bp"],
            chol=values["cholesterol"],
            weight=values["weight"],
            height=values["height"],
            save_to_db=values["save_to_db"],
            generate_pdf=values["generate_pdf"],
        )
    except Exception as exc:
        logger.error("AgeWell prediction failed (%s)", type(exc).__name__)
        return jsonify({"error": "Prediction could not be completed"}), 500

    return jsonify({
        "patient_id": result.patient_id,
        "risk": result.risk_label,
        "bmi": result.bmi,
        "health_score": result.health_score,
        "food_plan": result.food_plan,
        "exercise_plan": result.exercise_plan,
        "report_generated": result.pdf_file is not None,
        "email_sent": result.email_sent,
    })


@app.get("/records")
def records():
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "limit must be an integer between 1 and 100"}), 400
    if not 1 <= limit <= 100:
        return jsonify({"error": "limit must be an integer between 1 and 100"}), 400
    try:
        df = db.fetch_latest_records(limit=limit)
    except Exception as exc:
        logger.error("AgeWell record query failed (%s)", type(exc).__name__)
        return jsonify({"error": "Records could not be retrieved"}), 500
    return jsonify(df.to_dict(orient="records"))


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
