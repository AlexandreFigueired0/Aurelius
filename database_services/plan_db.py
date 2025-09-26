import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port='5432'
)


def get_plan_by_name(plan_name):
    cursor = conn.cursor()
    cursor.execute('SELECT id, price FROM plan WHERE plan_name = %s', (plan_name,))
    result = cursor.fetchone()
    cursor.close()
    return result  # Returns (id, price) or None if not found