import psycopg2
import os
from dotenv import load_dotenv
from . import plan_db
from . import server_plan_db

load_dotenv()  # Load environment variables from .env file

DISCORD_FREE_PLAN_NAME=os.getenv("DISCORD_FREE_PLAN_NAME", "Free")

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port='5432'
)

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
    server_plan_db.insert_server_plan(discord_server_id, DISCORD_FREE_PLAN_NAME)
    
    conn.commit()
    cursor.close()


def get_server_internal_id(discord_server_id):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM server WHERE server_id = %s', (discord_server_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


