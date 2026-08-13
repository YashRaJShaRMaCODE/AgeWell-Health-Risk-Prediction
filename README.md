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


## Project Structure

```
AgeWell/
├── app/
│   ├── routes/
│   │   └── api.py            # Flask REST API entry layer
│   ├── services/
│   │   ├── health_service.py # Business logic: BMI, score, recommendations, workflow
│   │   └── newpatient.py     # CLI entry point
│   ├── models/
│   │   ├── predictor.py      # Loads/serves the trained ML model
│   │   └── agewell_model.joblib
│   └── utils/
│       ├── db.py             # MySQL connection & queries
│       ├── pdf_report.py     # PDF report generation
│       └── email_utils.py    # High-risk email alerts
├── config/
│   ├── config.py             # Env-driven configuration
│   └── init_db.py            # Creates the health_records table
├── data/
│   └── agewell_data.csv
├── app.py                    # Streamlit UI entry point
├── requirements.txt
├── .env.example
└── README.md
```

## How to Run

1. Clone the repository
   ```
   git clone <repo-link>
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables
   ```
   cp .env.example .env
   # edit .env with your MySQL credentials and (optionally) email alert settings
   ```

4. Create the database schema
   ```
   python -m config.init_db
   ```

5. Run the application
   - Streamlit UI: `streamlit run app.py`
   - CLI: `python -m app.services.newpatient`
   - REST API: `python -m app.routes.api`

### Configuration

All secrets and environment-specific settings (DB credentials, email alert
credentials, model path) are read from environment variables via
`config/config.py` and `.env` — never hardcode credentials in source files.
See `.env.example` for the full list of variables.

