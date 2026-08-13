"""Central configuration for AgeWell, loaded from environment variables."""
import os

from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv("AGEWELL_MODEL_PATH", "app/models/agewell_model.joblib")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "agewell_db"),
}

EMAIL_CONFIG = {
    "sender": os.getenv("EMAIL_SENDER", ""),
    "receiver": os.getenv("EMAIL_RECEIVER", ""),
    "app_password": os.getenv("EMAIL_APP_PASSWORD", ""),
    "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "465")),
}

# When True, a patient predicted High Risk triggers an email alert (requires EMAIL_CONFIG to be set).
EMAIL_ALERTS_ENABLED = os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true"
