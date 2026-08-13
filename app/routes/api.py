"""Flask REST API entry layer for AgeWell (optional alternative to the Streamlit UI)."""
from flask import Flask, jsonify, request

from app.services.health_service import process_patient
from app.utils import db

app = Flask(__name__)


@app.post("/predict")
def predict():
    payload = request.get_json(force=True) or {}
    required = ["age", "heart_rate", "systolic_bp", "cholesterol", "weight", "height"]
    missing = [f for f in required if f not in payload]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        result = process_patient(
            age=int(payload["age"]),
            hr=int(payload["heart_rate"]),
            bp=int(payload["systolic_bp"]),
            chol=int(payload["cholesterol"]),
            weight=float(payload["weight"]),
            height=float(payload["height"]),
            save_to_db=bool(payload.get("save_to_db", True)),
            generate_pdf=bool(payload.get("generate_pdf", True)),
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "patient_id": result.patient_id,
        "risk": result.risk_label,
        "bmi": result.bmi,
        "health_score": result.health_score,
        "food_plan": result.food_plan,
        "exercise_plan": result.exercise_plan,
        "pdf_file": result.pdf_file,
        "email_sent": result.email_sent,
    })


@app.get("/records")
def records():
    limit = int(request.args.get("limit", 20))
    try:
        df = db.fetch_latest_records(limit=limit)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(df.to_dict(orient="records"))


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
