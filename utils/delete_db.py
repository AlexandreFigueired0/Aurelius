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


# Delete all tables
cursor.execute('DROP TABLE IF EXISTS stock cascade;')
cursor.execute('DROP TABLE IF EXISTS server cascade;')
cursor.execute('DROP TABLE IF EXISTS subscribed_stock cascade;')

conn.commit()
cursor.close()
conn.close()
print("All tables deleted.")
