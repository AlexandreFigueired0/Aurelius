import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import database_service as db

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix = '!', intents=intents)

def shorten_description(description):
    lines = description.split('.')
    MAX = 1024
    total_length = 0
    ret = ""
    for line in lines:
        if total_length + len(line) + 1 > MAX:
            break
        total_length += len(line) + 1
        ret += line + '.'
    return ret

def round_market_cap(market_cap):
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.2f}M"
    elif market_cap >= 1_000:
        return f"${market_cap / 1_000:.2f}K"
    else:
        return f"${market_cap}"

@bot.event
async def  on_ready():
    print(f"{bot.user.name} is ready")

@bot.event
async def on_message(message):
    if message.author == bot.user: return # Do not answer yourself

    
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")


@bot.command()
async def stock(ctx, arg):
    '''Fetch live stock  price, change %, market cap for a given ticker symbol.'''

    ticker = db.get_ticker_by_name(arg)
    if not ticker:
        await ctx.send(f"❌ Ticker symbol for '{arg}' not found.")
        return

    stock = yf.Ticker(ticker)
    info = stock.fast_info
    price = info.get("lastPrice", None)
    prev_close = info.get("previousClose", None)
    market_cap = round_market_cap(info.get("marketCap", 0))
    currency = info.get("currency", "USD")
    percent_change = round(((price - prev_close) / prev_close) * 100, 2)

    # --- Create an embed dashboard ---
    embed = discord.Embed(
        title=f"📊 {ticker} Stock Dashboard",
        description=f"Live stock information of **{ticker}**",
        color=discord.Color.green() if percent_change and percent_change >= 0 else discord.Color.red()
    )

    if price:
        embed.add_field(name="💵 Price", value=f"{price:.2f} {currency}", inline=True)
    if percent_change is not None:
        embed.add_field(name="📈 Change", value=f"{percent_change:.2f}%", inline=True)
    if market_cap:
        embed.add_field(name="🏦 Market Cap", value=market_cap, inline=True)

    embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")

    # --- Generate a price chart (last 1 month) ---
    hist = stock.history(period="1mo")
    if not hist.empty:
        # Modern style
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(9, 4))


        # Plot line
        line_color="#1f77b4"
        x = mdates.date2num(hist.index.to_pydatetime())
        y = hist["Close"].values
        ax.plot(x, y, color=line_color, linewidth=2)
        ax.fill_between(x, y, y.min(), color=line_color, alpha=0.1)

        # Title & labels
        ax.set_title(f"{ticker} - Last 1 Month", fontsize=14, weight="bold")
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel(f"Price ({currency})", fontsize=12)

        # Format dates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        fig.autofmt_xdate(rotation=30)

        # Clean up chart aesthetics
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("gray")
        ax.spines["bottom"].set_color("gray")
        ax.tick_params(axis="x", colors="gray")
        ax.tick_params(axis="y", colors="gray")

        # Remove top/right borders for a modern look
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Grid (subtle)
        ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.3)

        # Tight layout
        fig.tight_layout()

        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=150)
        buffer.seek(0)
        plt.close(fig)

        file = discord.File(buffer, filename=f"{ticker}_chart.png")
        embed.set_image(url=f"attachment://{ticker}_chart.png")

        await ctx.send(file=file, embed=embed)
    else:
        await ctx.send(embed=embed)


@bot.command()
async def info(ctx, arg):
    '''Fetch company information (description, sector, CEO, etc.) for a given ticker symbol.'''

    ticker = db.get_ticker_by_name(arg)
    if not ticker:
        await ctx.send(f"❌ Ticker symbol for '{arg}' not found.")
        return

    stock = yf.Ticker(ticker)
    info = stock.info
    description = info['longBusinessSummary']
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    company_oficcers = info.get('companyOfficers', 'N/A')
    ceo = "N/A"

    for officer in company_oficcers:
        if "ceo" in officer.get('title', '').lower() or "chief executive officer" in officer.get('title', '').lower():
            ceo = officer.get('name', 'N/A')
            break

        # --- Create an embed dashboard ---
    embed = discord.Embed(
        title=f"📊 {ticker} Info",
        description=f"Information of **{ticker}**",
        color=discord.Color.blue()
    )

    embed.add_field(name="🏢 Sector", value=sector, inline=True)
    embed.add_field(name="🏭 Industry", value=industry, inline=True)
    embed.add_field(name="👤 CEO", value=ceo, inline=True)
    embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")

    # If description is too long, send as file
    if len(description) > 1024:
        embed.add_field(name="Description", value=shorten_description(description), inline=False)
    else:
        embed.add_field(name="Description", value=description, inline=False)
    
    await ctx.send(embed=embed)


@bot.command()
async def chart(ctx, arg, period="1mo"):
    '''Fetch historical stock data for a given ticker symbol and period (default: 1 month).'''

    ticker = db.get_ticker_by_name(arg)
    if not ticker:
        await ctx.send(f"❌ Ticker symbol for '{arg}' not found.")
        return

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            await ctx.send(f"❌ No historical data found for **{ticker}** with period `{period}`.")
            return

        # Prepare data
        x = mdates.date2num(hist.index.to_pydatetime())
        y = hist["Close"].values
        start_price, end_price = y[0], y[-1]
        line_color = "#1f77b4"

        # Create chart
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(9, 4))

        ax.plot(x, y, color=line_color, linewidth=2)
        ax.fill_between(x, y, y.min(), color=line_color, alpha=0.1)

        ax.set_title(f"{ticker} - Last {period}", fontsize=14, weight="bold", color="white")
        ax.set_ylabel("Price (USD)", fontsize=12, color="white")

        # Format x-axis
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        fig.autofmt_xdate(rotation=30)

        # Aesthetics
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("gray")
        ax.spines["bottom"].set_color("gray")
        ax.tick_params(axis="x", colors="gray")
        ax.tick_params(axis="y", colors="gray")
        ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.3)

        fig.tight_layout()

        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png", dpi=150)
        buffer.seek(0)
        plt.close(fig)

        # Send chart to Discord
        file = discord.File(buffer, filename=f"{ticker}_chart.png")
        await ctx.send(file=file)

    except Exception as e:
        await ctx.send(f"⚠️ Error generating chart: {str(e)}")

@bot.command()
async def watch(ctx, arg, threshold: float = 10.0):
    '''Watch a stock and get notified when its price changes by a certain percentage (default: 10%).'''
    
    #check if server is stored in db, if not add it
    server_id = ctx.message.guild.id
    server_name = ctx.message.guild.name
    db.insert_server(server_id, server_name)
    ticker = db.get_ticker_by_name(arg)
    if not ticker:
        await ctx.send(f"❌ Ticker symbol for '{ticker}' not found.")
        return

    # Check if stock is already being watched
    subscribed_stocks = db.get_subscribed_stocks(server_id)
    for stock_id, change_percentage in subscribed_stocks:
        existing_ticker = db.get_ticker_by_id(stock_id)

        # Update threshold if the same stock is being watched with a different threshold
        if existing_ticker == ticker and change_percentage != abs(threshold):
            db.update_server_stock_threshold(server_id, ticker, abs(threshold))
            await ctx.send(f"✅ Updated notification threshold for **{ticker}** from {change_percentage}% to {abs(threshold)}%.")
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
    await ctx.send(f"✅ Stopped watching **{ticker}**.")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
db.close_connection()