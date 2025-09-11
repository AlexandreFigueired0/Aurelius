import psycopg2
import pandas as pd
import os

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DBNAME"),
    user=os.getenv("POSTGRES_USERNAME"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port='5432'
)

def get_ticker_by_name(company_name):
    cursor = conn.cursor()
    cursor.execute('SELECT ticker FROM stock WHERE name ILIKE %s', (f'%{company_name}%',))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


def close_connection():
    conn.close()