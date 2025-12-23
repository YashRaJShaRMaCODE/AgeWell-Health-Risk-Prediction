# AgeWell – Backend Health Risk Management System

AgeWell is a Python-based backend system designed to manage elderly health data,
perform risk scoring, and support backend workflows such as data storage,
processing, and reporting using a relational database.

This system helps caregivers make informed decisions through real-time analytics and personalized recommendations.
## System Architecture

The system follows a layered backend architecture:

- API / Entry Layer: Handles incoming requests and triggers backend workflows
- Service Layer: Contains business logic for patient data processing and risk evaluation
- Model Layer: Manages trained models and database-related structures
- Data Layer: Stores structured patient data in a relational database

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


## 📂 Project Structure

AgeWell/
├── app/
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic
│   ├── models/        # Model artifacts and schema-related logic
│   └── utils/         # Helper functions
├── data/              # Dataset files
├── config/            # Configuration files
├── app.py             # Application entry point
├── requirements.txt
└── README.md

## How to Run

1. Clone the repository
   git clone <repo-link>

2. Install dependencies
   pip install -r requirements.txt

3. Run the application
   python app.py

