import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import yfinance as yf
import matplotlib.dates as mdates
import database_service as db
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

STOCKS_ALERT_CHANNEL_NAME = "stock-alerts"
FREE_PLAN_MAX_WATCHED_STOCKS=int(os.getenv("FREE_PLAN_MAX_WATCHED_STOCKS", 5))
PRO_PLAN_MAX_WATCHED_STOCKS=int(os.getenv("PRO_PLAN_MAX_WATCHED_STOCKS", 50))


@bot.command()
async def watch(ctx, arg, threshold: float = 10.0):
    '''Watch a stock and get notified when its price changes by a certain percentage (default: 10%).'''

    
    #check if server is stored in db, if not add it
    server_id = ctx.message.guild.id
    ticker = db.get_ticker_by_name(arg)
    if not ticker:
        await ctx.send(f"❌ Ticker symbol for '{arg}' not found.")
        return

    subscribed_stocks = db.get_subscribed_stocks(server_id)

    # Check if server has reached the maximum number of watched stocks
    plan = db.get_server_plan(server_id)
    max_stocks = FREE_PLAN_MAX_WATCHED_STOCKS if not plan or plan[0] == "Free" else PRO_PLAN_MAX_WATCHED_STOCKS
    if len(subscribed_stocks) >= int(max_stocks):
        await ctx.send(f"❌ You have reached the maximum number of watched stocks ({max_stocks}) for your current plan ({plan[0] if plan else 'Free'}). Please upgrade your plan to watch more stocks.")
        return

    # Check if stock is already being watched
    for stock_id, change_percentage, alerted, last_alerted in subscribed_stocks:
        existing_ticker = db.get_ticker_by_id(stock_id)

        # Update threshold if the same stock is being watched with a different threshold
        if existing_ticker == ticker and change_percentage != abs(threshold):
            db.update_server_stock_threshold(server_id, ticker, abs(threshold))
            await ctx.send(f"✏️ Updated notification threshold for **{ticker}** from {change_percentage}% to {abs(threshold)}%.")
            return
        elif existing_ticker == ticker:
            await ctx.send(f"⚠️ Notifications for **{ticker}** are already set at {change_percentage}%.")
            return
        

    db.insert_server_stock(server_id, ticker, abs(threshold))
    await ctx.send(f"✅ Notifications for **{ticker}** when the price changes by {abs(threshold)}%.")

@bot.command()
async def unwatch(ctx, arg):
    '''Stop watching a stock.'''
    server_id = ctx.message.guild.id
    ticker = db.get_ticker_by_name(arg)
    if not ticker:
        await ctx.send(f"❌ Ticker symbol for '{arg}' not found.")
        return

    db.delete_server_stock(server_id, ticker)
    await ctx.send(f"🗑️ Stopped watching **{ticker}**.")

@bot.command()
async def unwatchall(ctx):
    '''Stop watching all stocks.'''
    server_id = ctx.message.guild.id
    stocks_ids = db.delete_server_stocks_from_server(server_id)
    embed = discord.Embed(
        title="🗑️ Unwatched All Stocks",
    )
    for stock_id in stocks_ids:
        ticker = db.get_ticker_by_id(stock_id)
        embed.add_field(name=ticker, value="Unwatched", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def list(ctx):
    '''List all watched stocks for this server.'''
    server_id = ctx.message.guild.id
    subscribed_stocks = db.get_subscribed_stocks(server_id)

    if not subscribed_stocks:
        await ctx.send("ℹ️ No stocks are currently being watched on this server.")
        return

    embed = discord.Embed(
        title="👀 Watched Stocks",
        description="Here are the stocks currently being watched on this server:",
        color=discord.Color.blue()
    )

    for stock_id, threshold, alerted, last_alerted in subscribed_stocks:
        ticker = db.get_ticker_by_id(stock_id)

        # If is alerted, point out
        if alerted:
            ticker = f"🚨 {ticker}"
        
        embed.add_field(name=ticker, value=f"Notification Threshold: {threshold}%", inline=False)

    await ctx.send(embed=embed)

@tasks.loop(minutes=1)
async def check_stock_percent_changes():
    '''Check stock price changes for all watched stocks and notify servers if thresholds are crossed.'''

    logger.info("Checking stock price changes...")

    for guild in bot.guilds:
        server_id = guild.id
        subscribed_stocks = db.get_subscribed_stocks(server_id)

        # If stock alert channel does not exist, create it
        channel = discord.utils.get(guild.text_channels, name=STOCKS_ALERT_CHANNEL_NAME)
        if not channel:
            # Create read-only channel for stock alerts
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=True),
                guild.me: discord.PermissionOverwrite(send_messages=True, view_channel=True)
            }
            channel = await guild.create_text_channel(STOCKS_ALERT_CHANNEL_NAME, overwrites=overwrites)
            
            await channel.send("📈 Stock price alerts are now active!")
            logger.info(f"Created channel: {STOCKS_ALERT_CHANNEL_NAME} in server: {guild.name} ({guild.id})")

        for stock_id, threshold, alerted, last_alerted in subscribed_stocks:
            ticker = db.get_ticker_by_id(stock_id)
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            price = info.get("lastPrice", None)
            prev_close = info.get("previousClose", None)

            percent_change = round(((price - prev_close) / prev_close) * 100, 2)
            if abs(percent_change) >= threshold:
                if not alerted:
                    embed = discord.Embed(
                        title=f"🚨 **{ticker}** Price Alert!",
                        description=f"The price of **{ticker}** has changed by {percent_change:.2f}% which is above your set threshold of {threshold}%.",
                        color=discord.Color.green() if percent_change >= 0 else discord.Color.red()
                    )
                    embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")
                    embed.add_field(name=ticker, value=f"Price: {price:.2f} USD\nChange: {percent_change:.2f}%", inline=False)
                    cur_message = await channel.send(embed=embed)
                    db.mark_stock_as_alerted(server_id, ticker)
            else: # Reset alert state if price goes back within threshold
                if alerted:
                    db.reset_stock_alert(server_id, ticker)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
db.close_connection()