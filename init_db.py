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
    UNIQUE (server_id, stock_id)
);
''')


# Check if stock table is empty before inserting initial data
cursor.execute('SELECT COUNT(*) FROM stock')
count = cursor.fetchone()[0]
if count > 0:
    print("Stock table already has data. Skipping initial data insertion.")
    # Print current entries in the stock table, with id, ticker, and name
    cursor.execute('SELECT id, ticker, name FROM stock')
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Ticker: {row[1]}, Name: {row[2]}")
else:
    # Fill Stock table with initial data from companies.csv
    companies = pd.read_csv('companies.csv')
    companies = companies[['company name', 'ticker']]

    for _, row in companies.iterrows():
        cursor.execute('''
        INSERT INTO stock (ticker, name)
        VALUES (%s, %s)
        ''', (row['ticker'], row['company name']))




conn.commit()
cursor.close()
conn.close()
