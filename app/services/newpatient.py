"""CLI entry point: enter a new patient's details, predict risk, save to
MySQL, generate a PDF report, and email an alert for high-risk patients."""
import pyttsx3

from app.services.health_service import process_patient
from app.utils import db


def main():
    db.init_db()

    print("\nEnter new patient details:\n")
    age = int(input("Age: "))
    hr = int(input("Heart Rate: "))
    bp = int(input("Systolic BP: "))
    chol = int(input("Cholesterol: "))
    weight = float(input("Weight (kg): "))
    height = float(input("Height (m): "))

    result = process_patient(age, hr, bp, chol, weight, height)

    print(f"\n✅ Predicted Risk: {result.risk_label}")
    print(f"📊 BMI: {result.bmi} | 🧮 Health Score: {result.health_score}")
    print(f"🥗 Food Plan: {result.food_plan}")
    print(f"💪 Exercise Plan: {result.exercise_plan}")
    if result.patient_id is not None:
        print(f"🧠 Saved to database. Patient ID: {result.patient_id}")
    if result.pdf_file:
        print(f"📄 PDF report generated: {result.pdf_file}")
    if result.email_sent:
        print("📧 High-risk alert email sent.")

    try:
        engine = pyttsx3.init()
        engine.say(
            f"The predicted risk is {result.risk_label}. "
            f"BMI is {result.bmi} and health score is {result.health_score}."
        )
        engine.runAndWait()
    except Exception:
        pass


if __name__ == "__main__":
    main()
