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

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix = '!', intents=intents)
companies = pd.read_csv('companies.csv')  # Assuming a CSV file with 'company name' and 'ticker' columns
# Trim DataFrame to necessary columns
companies = companies[['company name', 'ticker']]

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

def return_ticker(company_name):
    matches = companies[companies['company name'].str.lower().str.contains(company_name.lower())]
    if not matches.empty:
        return matches.iloc[0]['ticker']
    return None

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

    # Check if arg is a company name and convert to ticker if necessary
    if arg.upper() not in companies['ticker'].values:
        arg = return_ticker(arg)
        if not arg:
            await ctx.send(f"No ticker found for company name: {arg}")
            return

    stock = yf.Ticker(arg)
    info = stock.info
    price = round(info.get("currentPrice", None),2)
    # Round percent_change to 2 decimal places if it's a number
    percent_change = round(info.get("regularMarketChangePercent", None),2)
    market_cap = round_market_cap(info.get("marketCap", None))
    currency = info.get("currency", "USD")

    # --- Create an embed dashboard ---
    embed = discord.Embed(
        title=f"📊 {arg.upper()} Stock Dashboard",
        description=f"Live stock information of **{arg.upper()}**",
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
        ax.set_title(f"{arg.upper()} - Last 1 Month", fontsize=14, weight="bold")
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

        file = discord.File(buffer, filename=f"{arg}_chart.png")
        embed.set_image(url=f"attachment://{arg}_chart.png")

        await ctx.send(file=file, embed=embed)
    else:
        await ctx.send(embed=embed)


@bot.command()
async def info(ctx, arg):
    '''Fetch company information (description, sector, CEO, etc.) for a given ticker symbol.'''

    # Check if arg is a company name and convert to ticker if necessary
    if arg.upper() not in companies['ticker'].values:
        arg = return_ticker(arg)
        if not arg:
            await ctx.send(f"No ticker found for company name: {arg}")
            return

    stock = yf.Ticker(arg)
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
        title=f"📊 {arg.upper()} Info",
        description=f"Information of **{arg.upper()}**",
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
    # Check if arg is a company name and convert to ticker if necessary
    if arg.upper() not in companies['ticker'].values:
        arg = return_ticker(arg)
        if not arg:
            await ctx.send(f"No ticker found for company name: {arg}")
            return
    try:
        stock = yf.Ticker(arg)
        hist = stock.history(period=period)

        if hist.empty:
            await ctx.send(f"❌ No historical data found for **{arg.upper()}** with period `{period}`.")
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

        ax.set_title(f"{arg.upper()} - Last {period}", fontsize=14, weight="bold", color="white")
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
        file = discord.File(buffer, filename=f"{arg}_chart.png")
        await ctx.send(file=file)

    except Exception as e:
        await ctx.send(f"⚠️ Error generating chart: {str(e)}")



bot.run(token, log_handler=handler, log_level=logging.DEBUG) 