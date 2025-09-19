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

cursor = conn.cursor()


# Get entries of subscribed_stock table
cursor.execute('SELECT * FROM stock')
rows = cursor.fetchall()
for row in rows:
    print(row)