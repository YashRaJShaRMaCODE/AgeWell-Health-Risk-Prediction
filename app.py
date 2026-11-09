"""Streamlit UI entry point for AgeWell."""
import html
import logging
import os

import streamlit as st

from app.services.health_service import process_patient
from app.utils import db
from config.config import DB_CONFIGURED, EMAIL_ALERTS_ENABLED

logger = logging.getLogger(__name__)

st.set_page_config(page_title="AgeWell · Research Demo", page_icon="🩺", layout="wide")

st.markdown("""
<style>
:root{color-scheme:light;--ink:#183a33;--muted:#52665f;--paper:#f5f5ef;--leaf:#2f6d58;--amber:#e8ad4b}
.stApp{background:linear-gradient(145deg,#eef2eb 0%,var(--paper) 44%,#f8f7f2 100%);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
[data-testid="stMain"] .block-container{max-width:1120px;padding:2rem clamp(1rem,4vw,3.25rem) 4rem}
h1,h2,h3{color:var(--ink);letter-spacing:-.035em}
.agewell-hero{position:relative;overflow:hidden;margin:.2rem 0 1.7rem;padding:clamp(1.6rem,4vw,3.3rem);border-radius:18px;background:var(--ink);color:#fbfaf4}
.agewell-hero:after{position:absolute;right:-40px;top:-105px;width:310px;height:310px;border:1px solid #e8ad4b77;border-radius:50%;box-shadow:0 0 0 30px #e8ad4b12,0 0 0 60px #e8ad4b0b;content:"";pointer-events:none}
.agewell-hero__eyebrow{margin:0 0 .8rem;color:#d4e6d9;font-size:.72rem;font-weight:750;letter-spacing:.15em;text-transform:uppercase}
.agewell-hero h1{max-width:720px;margin:0;color:#fbfaf4;font-size:clamp(2.2rem,5.4vw,4.5rem);line-height:1.02;letter-spacing:-.055em}
.agewell-hero__summary{max-width:620px;margin:.9rem 0 0;color:#e2ebe5;font-size:1.05rem;line-height:1.6}
.agewell-hero__tag{display:inline-flex;margin-top:1.3rem;padding:.4rem .68rem;border:1px solid #e8ad4b80;border-radius:999px;color:#ffe0a4;font-size:.76rem;font-weight:650}
[data-testid="stAlert"]{border-radius:10px}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#dce5df!important;border-radius:14px;background:#ffffffc9}
div[data-testid="stButton"]>button,div[data-testid="stDownloadButton"]>button{min-height:44px;border-radius:8px;font-weight:700;transition:transform .18s ease,box-shadow .18s ease}
div[data-testid="stButton"]>button:hover,div[data-testid="stDownloadButton"]>button:hover{transform:translateY(-2px);box-shadow:0 8px 22px #173c351c}
div[data-testid="stButton"]>button:focus-visible,div[data-testid="stDownloadButton"]>button:focus-visible{outline:3px solid var(--amber);outline-offset:2px}
input,textarea,[data-baseweb="select"]>div{border-radius:8px!important}
.privacy-note{margin:-.45rem 0 1rem;padding:.85rem 1rem;border-left:3px solid var(--amber);background:#fff9e9;color:#51432a;font-size:.9rem;line-height:1.55}
@keyframes agewell-result{from{opacity:0;transform:translateY(10px) scale(.985)}to{opacity:1;transform:translateY(0) scale(1)}}
.prediction-result{margin:1rem 0;padding:1.25rem clamp(1rem,3vw,1.75rem);border:1px solid #dce5df;border-left:4px solid #3c8064;border-radius:12px;background:#fff;box-shadow:0 12px 32px #173c3510;animation:agewell-result .5s cubic-bezier(.2,.7,.2,1) both}
.prediction-result--high{border-left-color:#b45345}
.prediction-result__heading{margin:0 0 1rem;color:#53746b;font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase}
.prediction-result__metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:1.25rem}
.prediction-result__metric{display:grid;gap:4px;padding:12px 14px;border-radius:8px;background:#f3f7f4}
.prediction-result__metric span{color:#53746b;font-size:.72rem}
.prediction-result__metric strong{color:#173c35;font:650 1.35rem system-ui,sans-serif}
.prediction-result__advice{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;padding-top:1rem;border-top:1px solid #e3eae5}
.prediction-result__advice h4{margin:0 0 6px;color:#173c35;font:650 .9rem system-ui,sans-serif}
.prediction-result__advice p{margin:0;color:#53675f;font-size:.88rem;line-height:1.6}
@media(max-width:640px){[data-testid="stMain"] .block-container{padding-top:1rem}.agewell-hero:after{right:-180px;opacity:.65}.prediction-result__advice{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style>
""", unsafe_allow_html=True)

st.markdown("<section class='agewell-hero'><p class='agewell-hero__eyebrow'>AgeWell / Research prototype</p><h1>Health signals, made clearer.</h1><p class='agewell-hero__summary'>Explore how a research model responds to fictional sample values. This demo is not for clinical use.</p><span class='agewell-hero__tag'>Sample inputs only</span></section>", unsafe_allow_html=True)

st.warning(
    "Research demo only. Predictions and suggestions are not a diagnosis or medical advice. "
    "Do not use this app to make care decisions or enter real patient data."
)

st.subheader("Build a fictional sample")
st.markdown("<p class='privacy-note'>The hosted demo processes values to make an estimate. It does not save predictions to a database or send alerts. If you create a PDF, it is held temporarily on the host for download. Never enter real or identifying patient information.</p>", unsafe_allow_html=True)
synthetic_data_confirmed = st.checkbox(
    "I confirm these are fictional sample values, not real patient data."
)
c1, c2, c3 = st.columns(3)
with c1:
    age = st.number_input("Age (years)", min_value=40, max_value=120, value=70)
    hr = st.number_input("Heart rate (bpm)", min_value=30, max_value=200, value=80)
with c2:
    bp = st.number_input("Systolic blood pressure (mmHg)", min_value=80, max_value=250, value=130)
    chol = st.number_input("Cholesterol (mg/dL)", min_value=100, max_value=400, value=200)
with c3:
    weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, format="%.1f")
    height = st.number_input("Height (m)", min_value=1.0, max_value=2.2, value=1.68, format="%.2f")

st.write("")
colA, colB, colC = st.columns([1, 1, 2])
with colA:
    predict_btn = st.button("Predict", disabled=not synthetic_data_confirmed)
with colB:
    pdf_slot = st.empty()
with colC:
    insert_toggle = st.checkbox("Save record to MySQL", value=False, disabled=not DB_CONFIGURED)
    pdf_toggle = st.checkbox("Create a PDF report", value=False)
    alert_toggle = st.checkbox(
        "Email high-risk alert (requires saved record + PDF)",
        value=False,
        disabled=not (EMAIL_ALERTS_ENABLED and insert_toggle and pdf_toggle),
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

last_pdf = st.session_state.get("last_pdf")
pdf_ready = bool(last_pdf and os.path.isfile(last_pdf))
pdf_data = b""
if pdf_ready:
    with open(last_pdf, "rb") as report_file:
        pdf_data = report_file.read()
pdf_slot.download_button(
    "Download report PDF",
    data=pdf_data,
    file_name=os.path.basename(last_pdf) if pdf_ready else "AgeWell_Report.pdf",
    mime="application/pdf",
    disabled=not pdf_ready,
    help="Enable PDF report before predicting to create a downloadable report.",
)

st.markdown("---")

st.subheader("Optional local storage")
if not DB_CONFIGURED:
    st.info("Database storage is off for this demo. Sample predictions are not saved.")
elif st.button("Refresh table from DB"):
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
st.caption("AgeWell research demo · Fictional sample values only · Not a medical tool.")
