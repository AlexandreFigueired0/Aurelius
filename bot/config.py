# Bot configuration and shared instance
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

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

# Shared bot instance
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Constants
STOCKS_ALERT_CHANNEL_NAME = "stock-alerts"
FREE_PLAN_MAX_WATCHED_STOCKS = int(os.getenv("FREE_PLAN_MAX_WATCHED_STOCKS", 5))
PRO_PLAN_MAX_WATCHED_STOCKS = int(os.getenv("PRO_PLAN_MAX_WATCHED_STOCKS", 50))
NEWS_PER_PAGE = 5