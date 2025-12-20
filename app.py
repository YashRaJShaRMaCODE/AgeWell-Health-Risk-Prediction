# app.py
import streamlit as st
import joblib
import mysql.connector
from mysql.connector import Error
import pandas as pd
import io
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time

# CONFIG

st.set_page_config(page_title="AgeWell - Health Risk Predictor", layout="wide")
MODEL_PATH = "agewell_model.joblib"
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "210605",
    "database": "agewell_db"
}

INSERT_TO_DB = True

# UTILS

@st.cache_resource
def load_model(path):
    return joblib.load(path)

def connect_db(cfg):
    try:
        conn = mysql.connector.connect(**cfg)
        return conn
    except Error as e:
        return e

def convert_row_types(row_tuple):
    return (
        int(row_tuple[0]), int(row_tuple[1]), int(row_tuple[2]),
        int(row_tuple[3]), int(row_tuple[4]),
        float(row_tuple[5]), int(row_tuple[6]),
        str(row_tuple[7]), str(row_tuple[8])
    )

def generate_pdf(patient_id, age, hr, bp, chol, bmi, health_score, risk_label, food_plan, exercise_plan):
    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AgeWell - Patient Health Report", ln=True, align='C')
    pdf.ln(6)
    pdf.cell(0, 8, f"Patient ID: {patient_id}", ln=True)
    pdf.cell(0, 8, f"Age: {age}  |  Heart Rate: {hr}  |  BP: {bp}  |  Cholesterol: {chol}", ln=True)
    pdf.cell(0, 8, f"BMI: {bmi}  |  Health Score: {health_score}  |  Risk: {risk_label}", ln=True)
    pdf.ln(6)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, "Food Plan: " + food_plan)
    pdf.ln(3)
    pdf.multi_cell(0, 8, "Exercise Plan: " + exercise_plan)
    fname = f"AgeWell_Report_{patient_id}.pdf"
    pdf.output(fname)
    return fname


# LOAD MODEL

with st.spinner("Loading model..."):
    model = load_model(MODEL_PATH)
    time.sleep(0.3)


# header

col1, col2 = st.columns([8,2])
with col1:
    st.markdown("<h1 style='color:#0B6AFF; margin-bottom:2px;'>AgeWell — Elderly Health Risk Predictor</h1>", unsafe_allow_html=True)
    st.markdown("AI-powered predictions, recommendations and live storage.")
with col2:
    st.image("agewell_logo.png", width=120)

st.markdown("---")


# INPUTS

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
colA, colB, colC = st.columns([1,1,2])
with colA:
    predict_btn = st.button("Predict & Save")
with colB:
    pdf_btn = st.button("Download Last Report")
with colC:
    insert_toggle = st.checkbox("Enable DB insert (toggle)", value=INSERT_TO_DB)


# PREDICTION FLOW

if predict_btn:
    with st.spinner("Predicting..."):
        # ml predict
        raw_pred = model.predict([[age, hr, bp, chol]])[0]
        risk_label = "High Risk" if int(raw_pred)==1 else "Low Risk"

        bmi = round(weight / (height ** 2), 2)
        health_score = 100
        if bp > 140 or chol > 220:
            health_score -= 30
        if hr > 100:
            health_score -= 20
        if age > 70:
            health_score -= 10
        if int(raw_pred) == 1:
            health_score -= 20
        health_score = max(0, health_score)

        # Recommendations 
        if int(raw_pred) == 1:
            food = "Low-fat diet: oats, fruits, grilled veggies, avoid fried food."
            exercise = "Walk 30 min, breathing & light yoga."
        else:
            food = "Balanced diet: milk, nuts, rice, dal, vegetables."
            exercise = "Light jog, stretching, 20 min walk."

        st.success(f"Prediction: **{risk_label}**")
        st.write(f"**BMI:** {bmi}  |  **Health Score:** {health_score}")
        st.markdown("**Food Plan:** " + food)
        st.markdown("**Exercise Plan:** " + exercise)

        latest_patient_id = None
        # DB Insert
        if insert_toggle:
            conn = connect_db(DB_CONFIG)
            if isinstance(conn, Exception):
                st.error(f"DB Connection Error: {conn}")
            else:
                try:
                    cur = conn.cursor()
                    insert_q = """
                        INSERT INTO health_records
                        (age, heart_rate, systolic_bp, cholesterol, risk, bmi, health_score, food_chart, exercise_plan)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
                    cur.execute(insert_q, (
                        int(age), int(hr), int(bp), int(chol),
                        int(raw_pred),
                        float(bmi), int(health_score),
                        str(food), str(exercise)
                    ))
                    conn.commit()
                    cur.execute("SELECT LAST_INSERT_ID();")
                    latest_patient_id = cur.fetchone()[0]
                    st.success("✔ Data inserted into MySQL.")
                except Exception as e:
                    st.error(f"Insert Error: {e}")
                finally:
                    conn.close()

        # PDF
        pid_for_pdf = latest_patient_id if latest_patient_id else "temp"
        pdf_file = generate_pdf(pid_for_pdf, age, hr, bp, chol, bmi, health_score, risk_label, food, exercise)
        st.info(f"PDF generated: {pdf_file}")
        st.session_state["last_pdf"] = pdf_file

# DOWNLOAD PDF
if pdf_btn:
    if "last_pdf" in st.session_state:
        with open(st.session_state["last_pdf"], "rb") as f:
            st.download_button("Download report PDF", f, file_name=st.session_state["last_pdf"])
    else:
        st.warning("No report generated yet. Click Predict first.")

st.markdown("---")

st.subheader("Latest records (MySQL)")
if st.button("Refresh table from DB"):
    conn = connect_db(DB_CONFIG)
    if isinstance(conn, Exception):
        st.error(f"DB Connection Error: {conn}")
    else:
        try:
            df = pd.read_sql("SELECT * FROM health_records ORDER BY patient_id DESC LIMIT 20;", conn)
            st.dataframe(df)
            # BP trend
            if not df.empty:
                fig, ax = plt.subplots()
                sns.lineplot(x=df['patient_id'].astype(int), y=df['systolic_bp'].astype(float), marker="o", ax=ax)
                ax.set_title("Systolic BP (latest patients)")
                ax.set_xlabel("patient_id")
                ax.set_ylabel("systolic_bp")
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Query Error: {e}")
        finally:
            conn.close()

st.markdown("---")
st.caption("AgeWell — Enter new patient details, predict risk, download report, and optionally save to MySQL.")
