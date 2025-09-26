import psycopg2
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

def get_ticker_by_name(company_name):
    cursor = conn.cursor()
    # First check if the input is already a ticker
    cursor.execute('SELECT ticker FROM stock WHERE ticker = %s', (company_name.upper(),))
    result = cursor.fetchone()
    if result:
        result = result[0]
        cursor.close()
        return result

    # If not, search by exact company name match (case-insensitive)
    cursor.execute('SELECT ticker FROM stock WHERE name ILIKE %s', (company_name,))
    result = cursor.fetchone()
    if result:
        cursor.close()
        return result[0]
        
    # If still not found, search by partial company name match (case-insensitive)
    cursor.execute('SELECT ticker FROM stock WHERE name ILIKE %s', (f'%{company_name}%',))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


def get_stock_internal_id(ticker):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM stock WHERE ticker = %s', (ticker,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


def get_ticker_by_id(stock_id):
    cursor = conn.cursor()
    cursor.execute('SELECT ticker FROM stock WHERE id = %s', (stock_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

