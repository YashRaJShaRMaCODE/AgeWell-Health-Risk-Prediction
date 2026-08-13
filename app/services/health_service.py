"""Business logic: BMI/health score computation, recommendations, and the
end-to-end predict -> save -> report -> alert workflow."""
from dataclasses import dataclass

from app.models.predictor import predict_risk
from app.utils import db
from app.utils.email_utils import send_high_risk_alert
from app.utils.pdf_report import generate_health_report
from config.config import EMAIL_ALERTS_ENABLED


def compute_bmi(weight_kg: float, height_m: float) -> float:
    return round(weight_kg / (height_m ** 2), 2)


def compute_health_score(age, hr, bp, chol, risk: int) -> int:
    score = 100
    if bp > 140 or chol > 220:
        score -= 30
    if hr > 100:
        score -= 20
    if age > 70:
        score -= 10
    if risk == 1:
        score -= 20
    return max(0, score)


def get_food_chart(risk_label: str, bmi: float) -> str:
    if risk_label == "High":
        return (
            "Low-fat diet: oats, fruits, grilled veggies, no fried food."
            if bmi > 25 else
            "High-protein light diet: dal, fruits, boiled veggies."
        )
    return "Balanced diet: milk, nuts, rice, dal, and vegetables."


def get_exercise_plan(risk_label: str, bmi: float) -> str:
    if risk_label == "High":
        return "Morning walk (30 min), yoga, and breathing exercises daily."
    if bmi > 25:
        return "Brisk walk (40 min), cycling, avoid sitting long hours."
    return "Light jog, stretching, meditation, 20 min walk daily."


@dataclass
class PredictionResult:
    risk: int
    risk_label: str
    bmi: float
    health_score: int
    food_plan: str
    exercise_plan: str
    patient_id: int = None
    pdf_file: str = None
    email_sent: bool = False


def evaluate_patient(age, hr, bp, chol, weight, height) -> PredictionResult:
    """Run the ML model and derive BMI, score and recommendations (no I/O)."""
    risk = predict_risk(age, hr, bp, chol)
    risk_label = "High" if risk == 1 else "Low"
    bmi = compute_bmi(weight, height)
    health_score = compute_health_score(age, hr, bp, chol, risk)
    food_plan = get_food_chart(risk_label, bmi)
    exercise_plan = get_exercise_plan(risk_label, bmi)
    return PredictionResult(
        risk=risk, risk_label=risk_label, bmi=bmi, health_score=health_score,
        food_plan=food_plan, exercise_plan=exercise_plan,
    )


def process_patient(age, hr, bp, chol, weight, height, save_to_db=True,
                     generate_pdf=True, send_alert=None) -> PredictionResult:
    """Full workflow: predict, optionally persist to MySQL, generate a PDF
    report, and send an email alert for high-risk patients."""
    result = evaluate_patient(age, hr, bp, chol, weight, height)

    if send_alert is None:
        send_alert = EMAIL_ALERTS_ENABLED

    if save_to_db:
        patient_id = db.insert_record({
            "age": age, "heart_rate": hr, "systolic_bp": bp, "cholesterol": chol,
            "risk": result.risk, "bmi": result.bmi, "health_score": result.health_score,
            "food_chart": result.food_plan, "exercise_plan": result.exercise_plan,
        })
        result.patient_id = patient_id

    pid_for_report = result.patient_id if result.patient_id is not None else "temp"

    if generate_pdf:
        result.pdf_file = generate_health_report(
            pid_for_report, age, hr, bp, chol, result.bmi, result.health_score,
            result.risk_label, result.food_plan, result.exercise_plan,
        )

    if send_alert and result.risk == 1 and result.pdf_file and result.patient_id is not None:
        send_high_risk_alert(
            result.patient_id, age, hr, bp, chol, result.bmi, result.health_score,
            result.food_plan, result.exercise_plan, result.pdf_file,
        )
        db.mark_email_sent(result.patient_id)
        result.email_sent = True

    return result
