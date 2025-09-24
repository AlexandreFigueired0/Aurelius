import psycopg2
import pandas as pd
import os
from collect_stocks_names import get_ticker_name_dict



conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port='5432'
)

cursor = conn.cursor()

# Create Server table (Discord servers/guilds)
cursor.execute('''
CREATE TABLE IF NOT EXISTS server (
    id SERIAL PRIMARY KEY,
    server_id BIGINT UNIQUE NOT NULL,
    server_name VARCHAR(100)
);
''')

# Create Stock table
cursor.execute('''
CREATE TABLE IF NOT EXISTS stock (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(200)
);
''')

# Create SubscribedStock table (junction table - pure many-to-many)
cursor.execute('''
CREATE TABLE IF NOT EXISTS subscribed_stock (
    id SERIAL PRIMARY KEY,
    server_id INTEGER REFERENCES server(id) ON DELETE CASCADE,
    stock_id INTEGER REFERENCES stock(id) ON DELETE CASCADE,
    threshold DECIMAL(5,2) NOT NULL DEFAULT 10.0,
    alerted BOOLEAN NOT NULL DEFAULT FALSE,
    last_alerted TIMESTAMP NULL,
    UNIQUE (server_id, stock_id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS plan (
    id SERIAL PRIMARY KEY,
    plan_name VARCHAR(50) UNIQUE NOT NULL,
    price DECIMAL(6,2) NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS server_plan (
    id SERIAL PRIMARY KEY,
    server_id INTEGER NOT NULL REFERENCES server(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES plan(id) ON DELETE CASCADE,
    start_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_date TIMESTAMPTZ NULL,
    entitlement_id BIGINT UNIQUE,
    purchaser_user_id BIGINT,
    billing_platform VARCHAR(50),
    original_plan_name VARCHAR(50),
    UNIQUE (server_id)
);
''')

# Check if stock table is empty before inserting initial data
cursor.execute('SELECT COUNT(*) FROM stock')
count = cursor.fetchone()[0]
if count > 0:
    print("Stock table already has data. Skipping initial data insertion.")

else:
    # Fill Stock table with initial data from companies.csv
    companies = get_ticker_name_dict()
    df = pd.DataFrame(list(companies.items()), columns=['ticker', 'name'])
    for _, row in df.iterrows():
        cursor.execute('INSERT INTO stock (ticker, name) VALUES (%s, %s) ON CONFLICT (ticker) DO NOTHING', (row['ticker'], row['name']))

# Fill Plan table with initial plans
cursor.execute('SELECT COUNT(*) FROM plan')
count = cursor.fetchone()[0]
if count == 0:
    plans = [
        ('Free', 0.00),
        ('PRO', 4.99),
    ]
    for plan_name, price in plans:
        cursor.execute('INSERT INTO plan (plan_name, price) VALUES (%s, %s) ON CONFLICT (plan_name) DO NOTHING', (plan_name, price))
else:
    print("Plan table already has data. Skipping initial data insertion.")



conn.commit()
cursor.close()
conn.close()
