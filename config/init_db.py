"""Run this once to create the health_records table: python -m config.init_db"""
from app.utils.db import init_db

if __name__ == "__main__":
    init_db()
    print("✅ agewell_db schema is ready (health_records table created if missing).")
