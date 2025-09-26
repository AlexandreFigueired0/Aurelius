import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import yfinance as yf
import matplotlib.dates as mdates
from io import BytesIO
import database_service as db
from datetime import datetime, timezone
from utils.bot_helpers import build_plot, round_large_number, shorten_description
import logging


load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aurelius.log'),  # Your app logs
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger('aurelius')

bot = commands.Bot(command_prefix = '!', intents=intents, help_command=None)
NEWS_PER_PAGE = 5

STOCKS_ALERT_CHANNEL_NAME = "stock-alerts"
FREE_PLAN_MAX_WATCHED_STOCKS=int(os.getenv("FREE_PLAN_MAX_WATCHED_STOCKS", 5))
PRO_PLAN_MAX_WATCHED_STOCKS=int(os.getenv("PRO_PLAN_MAX_WATCHED_STOCKS", 50))
DISCORD_PRO_SERVER_SKU_ID=int(os.getenv("DISCORD_PRO_SERVER_SKU_ID"))
DISCORD_PRO_PLAN_NAME=os.getenv("DISCORD_PRO_PLAN_NAME", "PRO")
DISCORD_FREE_PLAN_NAME=os.getenv("DISCORD_FREE_PLAN_NAME", "Free")


@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} is ready")
    check_stock_percent_changes.start()

@bot.event
async def on_message(message):
    if message.author == bot.user: return # Do not answer yourself
    await bot.process_commands(message)
    
@bot.event
async def on_guild_join(guild):
    # When the bot joins a new server, ensure the server is in the database
    server_id = guild.id
    server_name = guild.name
    db.insert_server(server_id, server_name)

@bot.event
async def on_entitlement_create(entitlement):
    '''Handle Discord entitlement creation (when a user subscribes to a plan).'''
    sku_id = int(entitlement.sku_id)
    plan_name = db.SKU_ID_TO_PLAN.get(sku_id, None)
    if not plan_name:
        logger.warning(f"Unknown SKU ID: {sku_id}. No matching plan found.")
        return

    guild_id = int(entitlement.guild_id)
    user_id = int(entitlement.user_id)
    entitlement_id = int(entitlement.id)

    db.create_entitlement(guild_id, user_id, entitlement_id, plan_name)
    logger.info(f"Applied entitlement: Guild {guild_id}, User {user_id}, Plan {plan_name}")

@bot.event
async def on_entitlement_update(entitlement):
    '''Handle Discord entitlement updates (e.g., plan changes).'''
    sku_id = int(entitlement.sku_id)
    plan_name = db.SKU_ID_TO_PLAN.get(sku_id, None)
    if not plan_name:
        logger.warning(f"Unknown SKU ID: {sku_id}. No matching plan found.")
        return

    guild_id = int(entitlement.guild_id)
    user_id = int(entitlement.user_id)
    entitlement_id = int(entitlement.id)

    # Check if the entitlement is still active
    if entitlement.deleted:
        logger.warning(f"Entitlement {entitlement_id} is deleted. Revoking plan for Guild {guild_id}.")
        db.remove_entitlement(guild_id, entitlement_id)
    else: # Update/Renewal
        current_plan = db.get_server_plan(guild_id)
        if current_plan and current_plan[0] == plan_name:
            # Same plan, just a renewal
            logger.info(f"Renewing {plan_name} plan for Guild {guild_id}.")
            db.renew_entitlement(guild_id, entitlement_id)
        else:
            # Plan change
            db.create_entitlement(guild_id, user_id, entitlement_id, plan_name)
            logger.info(f"Changed entitlement: Guild {guild_id}, User {user_id}, Plan {plan_name}")


@bot.event
async def on_entitlement_delete(entitlement):
    '''Handle Discord entitlement deletion (when a user unsubscribes from a plan).'''
    guild_id = int(entitlement.guild_id)
    entitlement_id = int(entitlement.id)

    db.remove_entitlement(guild_id, entitlement_id)
    logger.info(f"Revoked entitlement: Guild {guild_id}, Entitlement ID {entitlement_id}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
db.close_connection()