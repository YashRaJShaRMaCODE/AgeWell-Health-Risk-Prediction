# 🧓 AgeWell – AI-Powered Elderly Health Monitoring System

AgeWell is a full-stack AI healthcare project designed to predict elderly patient health risk using Machine Learning, store results in a MySQL database, and visualize insights using a Power BI dashboard.

This system helps caregivers make informed decisions through real-time analytics and personalized recommendations.

---

## 🚀 Features

### 🔹 1. Machine Learning-Based Health Prediction
- Predicts **High / Low health risk**
- Calculates **BMI**
- Computes a **Health Score (0–100)**

### 🔹 2. Personalized Recommendations
- Diet plan based on BMI & risk  
- Exercise plan tailored to age and health score  

### 🔹 3. Database Integration (MySQL)
- Saves each patient’s records:
  - Age, Heart Rate, BP, Cholesterol  
  - BMI, Health Score  
  - Food & Exercise plan  
- Auto-increments patient ID

### 🔹 4. Power BI Dashboard (Analytics)
- Real-time insights after refresh
- KPIs (Avg BP, BMI, Risk Count)
- Line charts, scatter plots, donut charts
- Recommendation table

### 🔹 5. Streamlit Interface 
- User-friendly UI for entering patient data
- Shows prediction instantly
- Displays database records inside app
- Option to embed dashboard preview

---

## 🛠️ Tech Stack

| Component       | Technology Used |
|----------------|----------------|
| ML Model       | Logistic Regression (scikit-learn) |
| Backend        | Python 3 |
| Database       | MySQL |
| Visualization  | Power BI Desktop |
| Web UI         | Streamlit |
| Reporting      | FPDF (PDF Generator) |

---

## 📂 Project Structure

