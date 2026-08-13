"""MySQL connection and schema helpers for AgeWell."""
import mysql.connector
from mysql.connector import Error

from config.config import DB_CONFIG

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS health_records (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    age INT NOT NULL,
    heart_rate INT NOT NULL,
    systolic_bp INT NOT NULL,
    cholesterol INT NOT NULL,
    risk INT NOT NULL,
    bmi FLOAT NOT NULL,
    health_score INT NOT NULL,
    food_chart TEXT,
    exercise_plan TEXT,
    email_sent TINYINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection():
    """Return a live MySQL connection, or the raised Error if connecting failed."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as exc:
        return exc


def init_db():
    """Create the health_records table if it does not already exist."""
    conn = get_connection()
    if isinstance(conn, Exception):
        raise conn
    try:
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()


def insert_record(record: dict):
    """Insert a health record dict and return the new patient_id, or raise."""
    conn = get_connection()
    if isinstance(conn, Exception):
        raise conn
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO health_records
            (age, heart_rate, systolic_bp, cholesterol, risk, bmi, health_score, food_chart, exercise_plan, email_sent)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                record["age"], record["heart_rate"], record["systolic_bp"],
                record["cholesterol"], record["risk"], record["bmi"],
                record["health_score"], record["food_chart"],
                record["exercise_plan"], record.get("email_sent", 0),
            ),
        )
        conn.commit()
        cur.execute("SELECT LAST_INSERT_ID();")
        return cur.fetchone()[0]
    finally:
        conn.close()


def mark_email_sent(patient_id: int):
    conn = get_connection()
    if isinstance(conn, Exception):
        raise conn
    try:
        cur = conn.cursor()
        cur.execute("UPDATE health_records SET email_sent=1 WHERE patient_id=%s", (patient_id,))
        conn.commit()
    finally:
        conn.close()


def fetch_latest_records(limit: int = 20):
    import pandas as pd

    conn = get_connection()
    if isinstance(conn, Exception):
        raise conn
    try:
        return pd.read_sql(
            "SELECT * FROM health_records ORDER BY patient_id DESC LIMIT %s;", conn, params=(limit,)
        )
    finally:
        conn.close()
