import psycopg2
import os
import datetime
from dotenv import load_dotenv
from . import server_db
from . import plan_db

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

def insert_server_plan(discord_server_id, plan_name):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)
    plan = plan_db.get_plan_by_name(plan_name)
    plan_id = plan[0] if plan else None

    if not plan_id:
        cursor.close()
        raise ValueError("Plan not found")
    # Check if server already has a plan
    cursor.execute('SELECT id FROM server_plan WHERE server_id = %s', (server_id,))
    if cursor.fetchone():
        cursor.close()
        raise ValueError("Server already has a plan")
    cursor.execute('INSERT INTO server_plan (server_id, plan_id, original_plan_name) VALUES (%s, %s, %s)', (server_id, plan_id, plan_name))
    conn.commit()
    cursor.close()

def get_server_plan(discord_server_id):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)

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
    server_id = server_db.get_server_internal_id(discord_server_id)
    plan = plan_db.get_plan_by_name(new_plan_name)
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

def create_entitlement(discord_server_id, purchaser_user_id, entitlement_id, plan_name, billing_platform="Discord"):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)
    plan = plan_db.get_plan_by_name(plan_name)
    plan_id = plan[0] if plan else None
    if not plan_id:
        cursor.close()
        raise ValueError("Plan not found")
    
    # If entitlement_id already exists, do nothing
    cursor.execute('SELECT id FROM server_plan WHERE entitlement_id = %s', (entitlement_id,))
    if cursor.fetchone():
        cursor.close()
        return
    
    end_date = datetime.datetime.now() + datetime.timedelta(days=30)

    # Server always has a plan since we insert a Free plan on server creation
    cursor.execute('UPDATE server_plan \
                    SET plan_id = %s, \
                    entitlement_id = %s, \
                    purchaser_user_id = %s, \
                    billing_platform = %s, \
                    original_plan_name = %s, \
                    start_date = NOW(), \
                    end_date = %s \
                    WHERE server_id = %s',
                   (plan_id, entitlement_id, purchaser_user_id, billing_platform, plan_name, end_date, server_id))

    conn.commit()
    cursor.close()

def renew_entitlement(discord_server_id, entitlement_id):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)
    
    # Calculate new end_date (preserve start_date)
    end_date = datetime.datetime.now() + datetime.timedelta(days=30)
    
    cursor.execute('UPDATE server_plan \
                    SET end_date = %s \
                    WHERE server_id = %s AND entitlement_id = %s',
                   (end_date, server_id, entitlement_id))
    
    conn.commit()
    cursor.close()

def remove_entitlement(discord_server_id, entitlement_id):
    cursor = conn.cursor()
    server_id = server_db.get_server_internal_id(discord_server_id)
    free_plan = plan_db.get_plan_by_name('Free')
    free_plan_id = free_plan[0] if free_plan else None
    if not free_plan_id:
        cursor.close()
        raise ValueError("Free plan not found")
    
    # Put server back to Free plan
    cursor.execute('UPDATE server_plan \
                    SET plan_id = %s, \
                    entitlement_id = NULL, \
                    purchaser_user_id = NULL, \
                    billing_platform = NULL, \
                    original_plan_name = NULL, \
                    start_date = NOW(), \
                    end_date = NULL \
                    WHERE server_id = %s \
                    AND entitlement_id = %s',
                   (free_plan_id, server_id, entitlement_id))

    conn.commit()
    cursor.close()