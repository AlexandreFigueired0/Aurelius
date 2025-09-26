import psycopg2
import os
from dotenv import load_dotenv
import server_db
import stock_db

load_dotenv()  # Load environment variables from .env file

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port='5432'
)

def insert_server_stock(discord_server_id, ticker, threshold):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)
    stock_id = stock_db.get_stock_internal_id(ticker)

    cursor.execute('INSERT INTO subscribed_stock (server_id, stock_id, threshold) VALUES (%s, %s, %s)', (server_id, stock_id, threshold))
    conn.commit()
    cursor.close()

def get_subscribed_stocks(discord_server_id):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)

    cursor.execute('SELECT stock_id, threshold, alerted, last_alerted FROM subscribed_stock WHERE server_id = %s', (server_id,))
    results = cursor.fetchall()
    cursor.close()
    return results  # List of (stock_id, threshold, alerted, last_alerted) tuples


def update_server_stock_threshold(discord_server_id, ticker, new_threshold):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)
    stock_id = stock_db.get_stock_internal_id(ticker)

    cursor.execute('UPDATE subscribed_stock SET threshold = %s, alerted = FALSE, last_alerted = NULL WHERE server_id = %s AND stock_id = %s', (new_threshold, server_id, stock_id))
    conn.commit()
    cursor.close()


def delete_server_stock(discord_server_id, ticker):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)
    stock_id = stock_db.get_stock_internal_id(ticker)

    cursor.execute('DELETE FROM subscribed_stock WHERE server_id = %s AND stock_id = %s', (server_id, stock_id))
    conn.commit()
    cursor.close()

def delete_server_stocks_from_server(discord_server_id):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)

    cursor.execute('DELETE FROM subscribed_stock WHERE server_id = %s RETURNING stock_id', (server_id,))
    stocks = cursor.fetchall()
    conn.commit()
    cursor.close()
    return stocks

def mark_stock_as_alerted(discord_server_id, ticker):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)
    stock_id = stock_db.get_stock_internal_id(ticker)

    cursor.execute('UPDATE subscribed_stock SET alerted = TRUE, last_alerted = NOW() WHERE server_id = %s AND stock_id = %s', (server_id, stock_id))
    conn.commit()
    cursor.close()

def reset_stock_alert(discord_server_id, ticker):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)
    stock_id = stock_db.get_stock_internal_id(ticker)

    cursor.execute('UPDATE subscribed_stock SET alerted = FALSE, last_alerted = NULL WHERE server_id = %s AND stock_id = %s', (server_id, stock_id))
    conn.commit()
    cursor.close()

