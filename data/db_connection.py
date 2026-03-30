import mysql.connector
import pandas as pd

# Adjust these values to match your local setup
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "world_layoffs",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def query(sql: str, params=None) -> pd.DataFrame:
    """
    Run a SQL query and return a pandas DataFrame.
    """
    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn, params=params)
    finally:
        conn.close()
    return df

