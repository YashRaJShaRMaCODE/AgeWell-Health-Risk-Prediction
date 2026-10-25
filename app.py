"""Streamlit UI entry point for AgeWell."""
import html
import logging
import os

import streamlit as st

from app.services.health_service import process_patient
from app.utils import db
from config.config import EMAIL_ALERTS_ENABLED

logger = logging.getLogger(__name__)

st.set_page_config(page_title="AgeWell - Health Risk Predictor", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp{background:radial-gradient(ellipse at 90% 0,#d9e8e333,transparent 32%),#f5f7f5;color:#182a26;font-family:'DM Sans',sans-serif}
[data-testid="stMain"] .block-container{max-width:1180px;padding:2.5rem clamp(1rem,4vw,3.5rem) 4rem}
h1,h2,h3{font-family:'Manrope',sans-serif;letter-spacing:-.045em;color:#173c35}
[data-testid="stAlert"]{border-radius:12px}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#dce5df!important;border-radius:16px;background:#ffffffb8}
div.stButton>button,div.stDownloadButton>button{min-height:44px;border-radius:8px;font-weight:700;transition:transform .18s ease,box-shadow .18s ease}
div.stButton>button:hover,div.stDownloadButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 22px #173c351c}
input,textarea,[data-baseweb="select"]>div{border-radius:8px!important}
@keyframes agewell-result{from{opacity:0;transform:translateY(10px) scale(.985)}to{opacity:1;transform:translateY(0) scale(1)}}
.prediction-result{margin:1rem 0;padding:1.25rem clamp(1rem,3vw,1.75rem);border:1px solid #dce5df;border-left:4px solid #3c8064;border-radius:12px;background:#fff;box-shadow:0 12px 32px #173c3510;animation:agewell-result .5s cubic-bezier(.2,.7,.2,1) both}
.prediction-result--high{border-left-color:#b45345}
.prediction-result__heading{margin:0 0 1rem;color:#53746b;font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase}
.prediction-result__metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:1.25rem}
.prediction-result__metric{display:grid;gap:4px;padding:12px 14px;border-radius:8px;background:#f3f7f4}
.prediction-result__metric span{color:#53746b;font-size:.72rem}
.prediction-result__metric strong{color:#173c35;font:600 1.35rem 'Manrope',sans-serif}
.prediction-result__advice{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;padding-top:1rem;border-top:1px solid #e3eae5}
.prediction-result__advice h4{margin:0 0 6px;color:#173c35;font:650 .9rem 'Manrope',sans-serif}
.prediction-result__advice p{margin:0;color:#53675f;font-size:.88rem;line-height:1.6}
@media(max-width:640px){.prediction-result__advice{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style>
""", unsafe_allow_html=True)

LOGO_PATH = "assets/agewell_logo.png"

col1, col2 = st.columns([8, 2])
with col1:
    st.markdown("<p style='color:#53746b;font-size:.75rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;margin:0'>AGEWELL · RESEARCH PROTOTYPE</p><h1 style='margin:.3rem 0 .2rem'>Health signals, made clearer.</h1>", unsafe_allow_html=True)
    st.markdown("Explore a model estimate from sample inputs. This tool is not for clinical use.")
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
    predict_btn = st.button("Predict")
with colB:
    pdf_btn = st.button("Download Last Report")
with colC:
    insert_toggle = st.checkbox("Save record to MySQL", value=False)
    pdf_toggle = st.checkbox("Create a PDF report", value=False)
    alert_toggle = st.checkbox(
        "Email high-risk alert (requires saved record + PDF)",
        value=EMAIL_ALERTS_ENABLED,
        disabled=not (insert_toggle and pdf_toggle),
    )

if predict_btn:
    previous_pdf = st.session_state.pop("last_pdf", None)
    if previous_pdf and os.path.isfile(previous_pdf):
        os.remove(previous_pdf)
    with st.spinner("Predicting..."):
        try:
            result = process_patient(
                age, hr, bp, chol, weight, height,
                save_to_db=insert_toggle, generate_pdf=pdf_toggle, send_alert=alert_toggle,
            )
        except Exception:
            logger.exception("AgeWell prediction workflow failed")
            st.error("Prediction could not be completed. Check the server logs for details.")
            result = None

    if result:
        risk_style = "high" if result.risk == 1 else "low"
        st.markdown(f"""
        <section class="prediction-result prediction-result--{risk_style}" aria-label="Research model estimate">
          <p class="prediction-result__heading">Model estimate · not clinically validated</p>
          <div class="prediction-result__metrics">
            <div class="prediction-result__metric"><span>Estimated risk</span><strong>{html.escape(result.risk_label)} risk</strong></div>
            <div class="prediction-result__metric"><span>BMI · reference only</span><strong>{html.escape(str(result.bmi))}</strong></div>
            <div class="prediction-result__metric"><span>Prototype health score</span><strong>{html.escape(str(result.health_score))}</strong></div>
          </div>
          <div class="prediction-result__advice">
            <div><h4>Food plan</h4><p>{html.escape(result.food_plan)}</p></div>
            <div><h4>Exercise plan</h4><p>{html.escape(result.exercise_plan)}</p></div>
          </div>
        </section>
        """, unsafe_allow_html=True)

        if insert_toggle:
            if result.patient_id is not None:
                st.success(f"✔ Saved to MySQL. Patient ID: {result.patient_id}")
            else:
                st.error("DB insert failed — check DB_* environment variables and MySQL connectivity.")

        if result.pdf_file:
            st.info("PDF report generated. It is stored on this server until your next prediction.")
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
    except Exception:
        logger.exception("AgeWell records query failed")
        st.error("Records could not be loaded. Check the database configuration and server logs.")

st.markdown("---")
st.caption("AgeWell — Enter new patient details, predict risk, download report, and optionally save to MySQL.")
