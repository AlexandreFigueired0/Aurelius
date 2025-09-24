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


SKU_ID_TO_PLAN = {
    int(os.getenv("DISCORD_PRO_SERVER_SKU_ID")): os.getenv("DISCORD_PRO_PLAN_NAME", "PRO")
}

# conn = None

DISCORD_PRO_SERVER_SKU_ID=int(os.getenv("DISCORD_PRO_SERVER_SKU_ID"))
DISCORD_PRO_PLAN_NAME=os.getenv("DISCORD_PRO_PLAN_NAME", "PRO")
DISCORD_FREE_PLAN_NAME=os.getenv("DISCORD_FREE_PLAN_NAME", "Free")

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
    cursor.execute('INSERT INTO server (server_id, server_name) VALUES (%s, %s) RETURNING id', (discord_server_id, server_name))
    server_id = cursor.fetchone()[0]
    
    # Insert initial plan as 'Free'
    free_plan = get_plan_by_name('Free')
    server_id = get_server_internal_id(discord_server_id)
    cursor.execute('INSERT INTO server_plan (server_id, plan_id, original_plan_name) VALUES (%s, %s, %s)', (server_id, free_plan[0], 'Free'))
    
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

def delete_server_stocks_from_server(discord_server_id):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)

    cursor.execute('DELETE FROM subscribed_stock WHERE server_id = %s RETURNING stock_id', (server_id,))
    stocks = cursor.fetchall()
    conn.commit()
    cursor.close()
    return stocks

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

def get_plan_by_name(plan_name):
    cursor = conn.cursor()
    cursor.execute('SELECT id, price FROM plan WHERE plan_name = %s', (plan_name,))
    result = cursor.fetchone()
    cursor.close()
    return result  # Returns (id, price) or None if not found

def insert_server_plan(discord_server_id, plan_name):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)
    plan = get_plan_by_name(plan_name)
    plan_id = plan[0] if plan else None

    if not plan_id:
        cursor.close()
        raise ValueError("Plan not found")
    # Check if server already has a plan
    cursor.execute('SELECT id FROM server_plan WHERE server_id = %s', (server_id,))
    if cursor.fetchone():
        cursor.close()
        raise ValueError("Server already has a plan")
    cursor.execute('INSERT INTO server_plan (server_id, plan_id, ori) VALUES (%s, %s)', (server_id, plan_id))
    conn.commit()
    cursor.close()

def get_server_plan(discord_server_id):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)

    cursor.execute('''
        SELECT p.plan_name, p.price, sp.start_date, sp.end_date
        FROM server_plan sp
        JOIN plan p ON sp.plan_id = p.id
        WHERE sp.server_id = %s
    ''', (server_id,))
    result = cursor.fetchone()
    cursor.close()
    return result  # Returns (plan_name, price, start_date, end_date) or None if not found

def update_server_plan(discord_server_id, new_plan_name):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)
    plan = get_plan_by_name(new_plan_name)
    plan_id = plan[0] if plan else None

    if not plan_id:
        cursor.close()
        raise ValueError("Plan not found")
    
    # Check if server has a plan
    cursor.execute('SELECT id FROM server_plan WHERE server_id = %s', (server_id,))
    if not cursor.fetchone():
        cursor.close()
        raise ValueError("Server does not have a plan to update")
    
    cursor.execute('UPDATE server_plan SET plan_id = %s, start_date = NOW(), end_date = NULL WHERE server_id = %s', (plan_id, server_id))
    conn.commit()
    cursor.close()


def apply_entitlement(discord_server_id, purchaser_user_id, entitlement_id, plan_name, billing_platform="Discord"):
    cursor = conn.cursor()
    server_id = get_server_internal_id(discord_server_id)
    plan_name = SKU_ID_TO_PLAN.get(sku_id, None)
    if not plan_name:
        cursor.close()
        raise ValueError("Invalid SKU ID")
    plan = get_plan_by_name(plan_name)
    plan_id = plan[0] if plan else None
    if not plan_id:
        cursor.close()
        raise ValueError("Plan not found")
    
    # If entitlement_id already exists, do nothing
    cursor.execute('SELECT id FROM server_plan WHERE entitlement_id = %s', (entitlement_id,))
    if cursor.fetchone():
        cursor.close()
        return

    # Server always has a plan since we insert a Free plan on server creation
    cursor.execute('UPDATE server_plan \
                    SET plan_id = %s, \
                    entitlement_id = %s, \
                    purchaser_user_id = %s, \
                    billing_platform = %s, \
                    original_plan_name = %s \
                    WHERE server_id = %s',
                   (plan_id, entitlement_id, purchaser_user_id, billing_platform, plan_name, server_id))
    
    conn.commit()
    cursor.close()

def remove_entitlement(discord_server_id):

def close_connection():
    conn.close()