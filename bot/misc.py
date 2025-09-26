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
from helpers import build_plot, round_large_number, shorten_description
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


@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")





@bot.command()
async def help(ctx):
    '''Show help information for all commands.'''
    embed = discord.Embed(
        title="❓ Aurelius Help Menu",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )

    embed.add_field(name="!hello", value="Greet the bot.", inline=False)
    embed.add_field(name="!stock <ticker> [period]", value="Fetch live stock price, change %, market cap for a given ticker symbol and period (default: 1 month).", inline=False)
    embed.add_field(name="!info <ticker>", value="Fetch company information (description, sector, CEO, etc.) for a given ticker symbol.", inline=False)
    embed.add_field(name="!chart <ticker> [period]", value="Fetch historical stock data for a given ticker symbol and period (default: 1 month).", inline=False)
    embed.add_field(name="!watch <ticker> [threshold]", value="Watch a stock and get notified when its price changes by a certain percentage (default: 10%).", inline=False)
    embed.add_field(name="!unwatch <ticker>", value="Stop watching a stock.", inline=False)
    embed.add_field(name="!unwatchall", value="Stop watching all stocks.", inline=False)
    embed.add_field(name="!list", value="List all watched stocks for this server.", inline=False)
    embed.add_field(name="!news <ticker>", value="Fetch latest news articles for a given ticker symbol.", inline=False)
    embed.add_field(name="!metrics <ticker>", value="Fetch key financial metrics for a given ticker symbol.", inline=False)
    embed.add_field(name="!compare <ticker1> <ticker2> [period]", value="Compare historical stock data for two given ticker symbols and period (default: 1 year).", inline=False)
    embed.add_field(name="!compare_sp500 <ticker> [period]", value="Compare historical stock data for a given ticker symbol against S&P 500 index and period (default: 1 year).", inline=False)
    embed.add_field(name="!help", value="Show this help information.", inline=False)

    await ctx.send(embed=embed)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
db.close_connection()