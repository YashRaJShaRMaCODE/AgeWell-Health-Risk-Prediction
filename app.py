"""Streamlit UI entry point for AgeWell."""
import os

import streamlit as st

from app.services.health_service import process_patient
from app.utils import db
from config.config import EMAIL_ALERTS_ENABLED

st.set_page_config(page_title="AgeWell - Health Risk Predictor", layout="wide")

LOGO_PATH = "assets/agewell_logo.png"

col1, col2 = st.columns([8, 2])
with col1:
    st.markdown("<h1 style='color:#0B6AFF; margin-bottom:2px;'>AgeWell — Elderly Health Risk Predictor</h1>", unsafe_allow_html=True)
    st.markdown("Prototype risk estimates and optional record storage.")
with col2:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)

st.markdown("---")

st.warning(
    "Research demo only. Predictions and suggestions are not a diagnosis or medical advice. "
    "Do not use this app to make care decisions or enter real patient data."
)

st.subheader("Enter patient details")
c1, c2, c3 = st.columns(3)
with c1:
    age = st.number_input("Age", min_value=40, max_value=120, value=70)
    hr = st.number_input("Heart Rate", min_value=30, max_value=200, value=80)
with c2:
    bp = st.number_input("Systolic BP", min_value=80, max_value=250, value=130)
    chol = st.number_input("Cholesterol", min_value=100, max_value=400, value=200)
with c3:
    weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, format="%.1f")
    height = st.number_input("Height (m)", min_value=1.0, max_value=2.2, value=1.68, format="%.2f")

st.write("")
colA, colB, colC = st.columns([1, 1, 2])
with colA:
    predict_btn = st.button("Predict & Save")
with colB:
    pdf_btn = st.button("Download Last Report")
with colC:
    insert_toggle = st.checkbox("Enable DB insert", value=True)
    alert_toggle = st.checkbox("Send email alert on High Risk", value=EMAIL_ALERTS_ENABLED)

if predict_btn:
    with st.spinner("Predicting..."):
        try:
            result = process_patient(
                age, hr, bp, chol, weight, height,
                save_to_db=insert_toggle, generate_pdf=True, send_alert=alert_toggle,
            )
        except Exception as exc:
            st.error(f"Prediction failed: {exc}")
            result = None

    if result:
        st.success(f"Model estimate: **{result.risk_label} Risk** (not clinically validated)")
        st.write(f"**BMI:** {result.bmi}  |  **Health Score:** {result.health_score}")
        st.markdown("**Food Plan:** " + result.food_plan)
        st.markdown("**Exercise Plan:** " + result.exercise_plan)

        if insert_toggle:
            if result.patient_id is not None:
                st.success(f"✔ Saved to MySQL. Patient ID: {result.patient_id}")
            else:
                st.error("DB insert failed — check DB_* environment variables and MySQL connectivity.")

        if result.pdf_file:
            st.info(f"PDF generated: {result.pdf_file}")
            st.session_state["last_pdf"] = result.pdf_file

        if alert_toggle and result.risk == 1:
            if result.email_sent:
                st.success("📧 High-risk alert email sent.")
            else:
                st.warning("Email alert not sent — check EMAIL_* environment variables.")

if pdf_btn:
    if "last_pdf" in st.session_state and os.path.exists(st.session_state["last_pdf"]):
        with open(st.session_state["last_pdf"], "rb") as f:
            st.download_button("Download report PDF", f, file_name=os.path.basename(st.session_state["last_pdf"]))
    else:
        st.warning("No report generated yet. Click Predict first.")

st.markdown("---")

st.subheader("Latest records (MySQL)")
if st.button("Refresh table from DB"):
    try:
        df = db.fetch_latest_records(limit=20)
        st.dataframe(df)
        if not df.empty:
            import matplotlib.pyplot as plt
            import seaborn as sns

            fig, ax = plt.subplots()
            sns.lineplot(x=df["patient_id"].astype(int), y=df["systolic_bp"].astype(float), marker="o", ax=ax)
            ax.set_title("Systolic BP (latest patients)")
            ax.set_xlabel("patient_id")
            ax.set_ylabel("systolic_bp")
            st.pyplot(fig)
    except Exception as exc:
        st.error(f"Query Error: {exc}")

st.markdown("---")
st.caption("AgeWell — Enter new patient details, predict risk, download report, and optionally save to MySQL.")
