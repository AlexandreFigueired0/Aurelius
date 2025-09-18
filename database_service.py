import psycopg2
import pandas as pd
import os

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port='5432'
)

# conn = None

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

def insert_server(discord_server_id, server_name):
    cursor = conn.cursor()
    # Check if server already exists
    cursor.execute('SELECT id FROM server WHERE server_id = %s', (discord_server_id,))
    if cursor.fetchone():
        cursor.close()
        return  # Server already exists

    # Insert new server
    cursor.execute('INSERT INTO server (server_id, server_name) VALUES (%s, %s)', (discord_server_id, server_name))
    conn.commit()
    cursor.close()

def insert_server_stock(discord_server_id, ticker, threshold):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)
    stock_id = get_stock_internal_id(ticker)

    cursor.execute('INSERT INTO subscribed_stock (server_id, stock_id, threshold) VALUES (%s, %s, %s)', (server_id, stock_id, threshold))
    conn.commit()
    cursor.close()

def get_stock_internal_id(ticker):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM stock WHERE ticker = %s', (ticker,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def get_server_internal_id(discord_server_id):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM server WHERE server_id = %s', (discord_server_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def get_subscribed_stocks(discord_server_id):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)

    cursor.execute('SELECT stock_id, threshold, alerted, last_alerted FROM subscribed_stock WHERE server_id = %s', (server_id,))
    results = cursor.fetchall()
    cursor.close()
    return results  # List of (stock_id, threshold, alerted, last_alerted) tuples


def get_ticker_by_id(stock_id):
    cursor = conn.cursor()
    cursor.execute('SELECT ticker FROM stock WHERE id = %s', (stock_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None

def update_server_stock_threshold(discord_server_id, ticker, new_threshold):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)
    stock_id = get_stock_internal_id(ticker)

    cursor.execute('UPDATE subscribed_stock SET threshold = %s, alerted = FALSE, last_alerted = NULL WHERE server_id = %s AND stock_id = %s', (new_threshold, server_id, stock_id))
    conn.commit()
    cursor.close()

def delete_server_stock(discord_server_id, ticker):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)
    stock_id = get_stock_internal_id(ticker)

    cursor.execute('DELETE FROM subscribed_stock WHERE server_id = %s AND stock_id = %s', (server_id, stock_id))
    conn.commit()
    cursor.close()


def mark_stock_as_alerted(discord_server_id, ticker):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)
    stock_id = get_stock_internal_id(ticker)

    cursor.execute('UPDATE subscribed_stock SET alerted = TRUE, last_alerted = NOW() WHERE server_id = %s AND stock_id = %s', (server_id, stock_id))
    conn.commit()
    cursor.close()

def reset_stock_alert(discord_server_id, ticker):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)
    stock_id = get_stock_internal_id(ticker)

    cursor.execute('UPDATE subscribed_stock SET alerted = FALSE, last_alerted = NULL WHERE server_id = %s AND stock_id = %s', (server_id, stock_id))
    conn.commit()
    cursor.close()

def close_connection():
    conn.close()