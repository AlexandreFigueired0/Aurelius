import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import database_service as db
from datetime import datetime, timezone

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix = '!', intents=intents, help_command=None)
NEWS_PER_PAGE = 5

STOCKS_ALERT_CHANNEL_NAME = "stock-alerts"

def simple_iv_calculation(ev, shares_outstanding):
    return round(ev / shares_outstanding, 2)

def dcf_iv_calculation(fcf, revenue_growth, shares_outstanding, years=5, discount_rate=0.10, terminal_growth=0.03):
    fcf_projections = []
    total_pv = 0

    # Project FCF for n years
    for year in range(1, years + 1):
        fcf *= (1 + revenue_growth)  # grow FCF
        fcf_projections.append(fcf)
        total_pv += fcf / ((1 + discount_rate) ** year)

    # Terminal Value
    terminal_fcf = fcf_projections[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)
    terminal_pv = terminal_value / ((1 + discount_rate) ** years)

    # Enterprise Value (sum of PVs)
    iv_dcf = round((total_pv + terminal_pv) / shares_outstanding, 2)
    return iv_dcf

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

def round_large_number(number):
    """Format large numbers with suffixes (K, M, B, T)."""
    if number >= 1_000_000_000_000:
        return f"{number / 1_000_000_000_000:.2f}T"
    elif number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return f"{number}"

@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready")
    check_stock_percent_changes.start()

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
    market_cap = round_large_number(info.get("marketCap", 0))
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
        embed.add_field(name="🏦 Market Cap", value=f"${market_cap}", inline=True)

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
        await ctx.send(f"❌ Ticker symbol for '{arg}' not found.")
        return

    # Check if stock is already being watched
    subscribed_stocks = db.get_subscribed_stocks(server_id)
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
        embed.add_field(name=ticker, value=f"Notification Threshold: {threshold}%", inline=False)

    await ctx.send(embed=embed)

@tasks.loop(minutes=1)
async def check_stock_percent_changes():
    '''Check stock price changes for all watched stocks and notify servers if thresholds are crossed.'''

    print("Checking stock price changes...")

    for guild in bot.guilds:
        embed = discord.Embed(
            title="🔔 Stock Price Alert",
            description=f"The following stocks have crossed their notification thresholds:",
            color=discord.Color.yellow()
        )
        embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")
        server_id = guild.id
        subscribed_stocks = db.get_subscribed_stocks(server_id)
        count = 0

        for stock_id, threshold, alerted, last_alerted in subscribed_stocks:
            ticker = db.get_ticker_by_id(stock_id)
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            price = info.get("lastPrice", None)
            prev_close = info.get("previousClose", None)

            percent_change = round(((price - prev_close) / prev_close) * 100, 2)
            if abs(percent_change) >= threshold:
                if not alerted:
                    embed.add_field(name=ticker, value=f"Price: {price:.2f} USD\nChange: {percent_change:.2f}%", inline=False)
                    count += 1
                    db.mark_stock_as_alerted(server_id, ticker)
            else: # Reset alert state if price goes back within threshold
                if alerted:
                    db.reset_stock_alert(server_id, ticker)

        channel = discord.utils.get(guild.text_channels, name=STOCKS_ALERT_CHANNEL_NAME)
        # Send message to stock alert channel, if channel does not exist, create it
        if not channel:
            # Create read-only channel for stock alerts
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=True),
                guild.me: discord.PermissionOverwrite(send_messages=True, view_channel=True)
            }
            channel = await guild.create_text_channel(STOCKS_ALERT_CHANNEL_NAME, overwrites=overwrites)
            
            await channel.send("📈 Stock price alerts are now active!")
            print(f"Created channel: {STOCKS_ALERT_CHANNEL_NAME} in server: {guild.name} ({guild.id})")

        if count > 0:
            await channel.send(embed=embed)

@bot.command()
async def help(ctx):
    '''Show help information for all commands.'''
    embed = discord.Embed(
        title="❓ Aurelius Help Menu",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )

    embed.add_field(name="!hello", value="Greet the bot.", inline=False)
    embed.add_field(name="!stock <ticker>", value="Fetch live stock price, change %, market cap for a given ticker symbol.", inline=False)
    embed.add_field(name="!info <ticker>", value="Fetch company information (description, sector, CEO, etc.) for a given ticker symbol.", inline=False)
    embed.add_field(name="!chart <ticker> [period]", value="Fetch historical stock data for a given ticker symbol and period (default: 1 month).", inline=False)
    embed.add_field(name="!watch <ticker> [threshold]", value="Watch a stock and get notified when its price changes by a certain percentage (default: 10%).", inline=False)
    embed.add_field(name="!unwatch <ticker>", value="Stop watching a stock.", inline=False)
    embed.add_field(name="!list", value="List all watched stocks for this server.", inline=False)
    embed.add_field(name="!news <ticker>", value="Fetch latest news articles for a given ticker symbol.", inline=False)
    embed.add_field(name="!metrics <ticker>", value="Fetch key financial metrics for a given ticker symbol.", inline=False)
    embed.add_field(name="!help", value="Show this help information.", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def news(ctx, arg):
    '''Fetch latest news articles for a given ticker symbol.'''


    ticker = db.get_ticker_by_name(arg)
    if not ticker:
        await ctx.send(f"❌ Ticker symbol for '{arg}' not found.")
        return
    
    stock = yf.Ticker(ticker)
    news_items = stock.news
    n_pages = -(len(news_items) // -NEWS_PER_PAGE)  # Ceiling division
   
    if not news_items:
        await ctx.send(f"❌ No news articles found for '{ticker}'.")
        return
    

    def build_embed(page_number):
        # Calculate ceiling of news items / NEWS_PER_PAGE
        embed = discord.Embed(
            title=f"Latest News for {ticker} (Page {page_number}/{n_pages})",
            color=discord.Color.blue()
        )

        for item in news_items[NEWS_PER_PAGE * (page_number - 1): NEWS_PER_PAGE * page_number]:
            content = item["content"]
            date_str = content['pubDate'].replace("T", " ").replace("Z", " ")
            embed.add_field(name=content['title'], value=f"{content['summary']}\nPublished on: {date_str}\n[Read more]({content['canonicalUrl']['url']})", inline=False)
        embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")
        return embed
    
    next_page_reaction = "▶️"
    page = 1
    cur_message = await ctx.send(embed=build_embed(page))

    if n_pages > 1:
        await cur_message.add_reaction(next_page_reaction)

    def check(reaction, user):
        return (
            user == ctx.author
            and reaction.message.id == cur_message.id
            and str(reaction.emoji) == "▶️"
        )

    member = ctx.author

    page += 1
    while page <= n_pages:
        reaction, user = await bot.wait_for("reaction_add",  check=check)

        next_message = await ctx.send(embed=build_embed(page))

        if page < n_pages:
            await next_message.add_reaction(next_page_reaction)

        cur_message = next_message
        page += 1

@bot.command()
async def metrics(ctx, arg):
    '''Fetch key financial metrics for a given ticker symbol.'''

    ticker = db.get_ticker_by_name(arg)
    if not ticker:
        await ctx.send(f"❌ Ticker symbol for '{arg}' not found.")
        return
    stock = yf.Ticker(ticker)
    info = stock.get_info()
    if not info:
        await ctx.send(f"❌ No financial metrics found for '{ticker}'.")
        return
    

    ev = info.get("enterpriseValue", None)
    trailing_pe = info.get("trailingPE", None)
    forward_pe = info.get("forwardPE", None)
    dividend_yield = info.get("dividendYield", None)
    price_to_book = info.get("priceToBook", None)
    beta = info.get("beta", None)
    target_high = info.get("targetHighPrice", None)
    target_low = info.get("targetLowPrice", None)
    target_mean = info.get("targetMeanPrice", None)
    recommendation = info.get("recommendationKey", None)

    earnings_growth = info.get("earningsGrowth", None)
    shares_outstanding = info.get("sharesOutstanding", None)
    revenue_growth = info.get("revenueGrowth", None)
    fcf = info.get("freeCashflow", None)
    iv_simple = ev / shares_outstanding
    fcf_projections = []
    years = 5
    discount_rate = 0.10
    total_pv = 0
    terminal_growth = 0.03

    # iv_simple = simple_iv_calculation(ev, shares_outstanding)
    # iv_dcf = dcf_iv_calculation(fcf, revenue_growth, shares_outstanding, years, discount_rate, terminal_growth)

    # --- Create an embed dashboard ---
    embed = discord.Embed(
        title=f"📊 {ticker} Key Financial Metrics",
        description=f"Key financial metrics of **{ticker}**"
    )
    embed.add_field(name="💼 Enterprise Value (EV)", value=f"${round_large_number(ev)}" if ev else "N/A", inline=True)
    embed.add_field(name="📊 Trailing P/E", value=f"{trailing_pe:.2f}" if trailing_pe else "N/A", inline=True)
    embed.add_field(name="🔮 Forward P/E", value=f"{forward_pe:.2f}" if forward_pe else "N/A", inline=True)
    embed.add_field(name="💰 Dividend Yield", value=f"{dividend_yield:.2f}%" if dividend_yield else "N/A", inline=True)
    embed.add_field(name="🏦 Price to Book", value=f"{price_to_book:.2f}" if price_to_book else "N/A", inline=True)
    embed.add_field(name="🎯 Target Price (High)", value=f"${target_high:,.2f}" if target_high else "N/A", inline=True)
    embed.add_field(name="🎯 Target Price (Low)", value=f"${target_low:,.2f}" if target_low else "N/A", inline=True)
    embed.add_field(name="🎯 Target Price (Mean)", value=f"${target_mean:,.2f}" if target_mean else "N/A", inline=True)
    embed.add_field(name="📈 Beta", value=f"{beta:.2f}" if beta else "N/A", inline=True)
    embed.add_field(name="📝 Recommendation", value=recommendation.capitalize() if recommendation else "N/A", inline=True)

    embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")
    await ctx.send(embed=embed)



bot.run(token, log_handler=handler, log_level=logging.DEBUG)
db.close_connection()