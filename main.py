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

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix = '!', intents=intents, help_command=None)
NEWS_PER_PAGE = 5

STOCKS_ALERT_CHANNEL_NAME = "stock-alerts"



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
async def stock(ctx, arg, period="1mo"):
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

    embed.add_field(name="💵 Price", value=f"{price:.2f} {currency}", inline=True)
    embed.add_field(name="📈 Change", value=f"{percent_change:.2f}%", inline=True)
    embed.add_field(name="🏦 Market Cap", value=f"${market_cap}", inline=True)
    embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")

    hist = stock.history(period=period)
    if hist.empty:
        await ctx.send(f"❌ No historical data found for **{ticker}** with period `{period}`.")
        return

    line_color="#1f77b4"
    x = mdates.date2num(hist.index.to_pydatetime())
    y = hist["Close"].values
    buffer = build_plot([(x,y)], f"{ticker} - Last 1 Month", "Date", "Price (USD)", [ticker], [line_color])
    file = discord.File(buffer, filename="chart.png")
    embed.set_image(url="attachment://chart.png")
    await ctx.send(file=file, embed=embed)

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


        line_color="#1f77b4"
        x = mdates.date2num(hist.index.to_pydatetime())
        y = hist["Close"].values
        buffer = build_plot([(x,y)], f"{ticker} - Last 1 Month", "Date", "Price (USD)", [ticker], [line_color])
        file = discord.File(buffer, filename="chart.png")

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

    print("Checking stock price changes...")

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
            print(f"Created channel: {STOCKS_ALERT_CHANNEL_NAME} in server: {guild.name} ({guild.id})")

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
    embed.add_field(name="!list", value="List all watched stocks for this server.", inline=False)
    embed.add_field(name="!news <ticker>", value="Fetch latest news articles for a given ticker symbol.", inline=False)
    embed.add_field(name="!metrics <ticker>", value="Fetch key financial metrics for a given ticker symbol.", inline=False)
    embed.add_field(name="!compare <ticker1> <ticker2> [period]", value="Compare historical stock data for two given ticker symbols and period (default: 1 year).", inline=False)
    embed.add_field(name="!compare_sp500 <ticker> [period]", value="Compare historical stock data for a given ticker symbol against S&P 500 index and period (default: 1 year).", inline=False)
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


@bot.command()
async def compare(ctx, arg1, arg2, period="1y"):
    '''Compare historical stock data for two given ticker symbols and period (default: 1 month).'''

    ticker1 = db.get_ticker_by_name(arg1)
    ticker2 = db.get_ticker_by_name(arg2)
    if not ticker1:
        await ctx.send(f"❌ Ticker symbol for '{arg1}' not found.")
        return
    if not ticker2:
        await ctx.send(f"❌ Ticker symbol for '{arg2}' not found.")
        return

    try:
        stock1 = yf.Ticker(ticker1)
        stock2 = yf.Ticker(ticker2)
        hist1 = stock1.history(period=period)
        hist2 = stock2.history(period=period)

        if hist1.empty:
            await ctx.send(f"❌ No historical data found for **{ticker1}** with period `{period}`.")
            return
        if hist2.empty:
            await ctx.send(f"❌ No historical data found for **{ticker2}** with period `{period}`.")
            return

        # Prepare data
        x1 = mdates.date2num(hist1.index.to_pydatetime())
        y1 = hist1["Close"].values
        x2 = mdates.date2num(hist2.index.to_pydatetime())
        y2 = hist2["Close"].values
        buffer = build_plot([(x1, y1), (x2, y2)], 
        f"{ticker1} vs {ticker2} - Last {period}", "Date", "Price (USD)", [ticker1, ticker2], ["#1f77b4", "#ff7f0e"])
        # create embed
        embed = discord.Embed(
            title=f"📊 {ticker1} vs {ticker2} Comparison",
            description=f"Comparison of **{ticker1}** and **{ticker2}**",
            color=0x1f77b4
        )
        # Set footer
        embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")
        # Compare key metrics
        info1 = stock1.info
        info2 = stock2.info
        market_cap1 = info1.get("marketCap", None)
        market_cap2 = info2.get("marketCap", None)
        pe1 = info1.get("trailingPE", None)
        pe2 = info2.get("trailingPE", None)
        dividend_yield1 = info1.get("dividendYield", 0)
        dividend_yield2 = info2.get("dividendYield", 0)
        beta1 = info1.get("beta", None)
        beta2 = info2.get("beta", None)
        embed.add_field(name="🏦 Market Cap", value=f"{ticker1}: ${round_large_number(market_cap1)}\n{ticker2}: ${round_large_number(market_cap2)}" if market_cap1 and market_cap2 else "N/A", inline=True)
        embed.add_field(name="📊 Trailing P/E", value=f"{ticker1}: {pe1:.2f}\n{ticker2}: {pe2:.2f}" if pe1 and pe2 else "N/A", inline=True)
        embed.add_field(name="💰 Dividend Yield", value=f"{ticker1}: {dividend_yield1:.2f}%\n{ticker2}: {dividend_yield2:.2f}%", inline=True)
        embed.add_field(name="📈 Beta", value=f"{ticker1}: {beta1:.2f}\n{ticker2}: {beta2:.2f}" if beta1 and beta2 else "N/A", inline=True)
        

        file = discord.File(buffer, filename="chart.png")
        embed.set_image(url="attachment://chart.png")
        await ctx.send(file=file, embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Error generating comparison chart: {str(e)}")

# Function to compare stock against s&p 500
@bot.command()
async def compare_sp500(ctx, arg, period="1y"):
    '''Compare historical stock data for a given ticker symbol against S&P 500 index and period (default: 1 year).'''

    ticker = db.get_ticker_by_name(arg)
    sp500_ticker = "^GSPC"  # Yahoo Finance ticker for S&P 500
    if not ticker:
        await ctx.send(f"❌ Ticker symbol for '{arg}' not found.")
        return

    try:
        stock = yf.Ticker(ticker)
        sp500 = yf.Ticker(sp500_ticker)
        hist_stock = stock.history(period=period)
        hist_sp500 = sp500.history(period=period)

        if hist_stock.empty:
            await ctx.send(f"❌ No historical data found for **{ticker}** with period `{period}`.")
            return
        if hist_sp500.empty:
            await ctx.send(f"❌ No historical data found for S&P 500 with period `{period}`.")
            return

        # Prepare data
        x_stock = mdates.date2num(hist_stock.index.to_pydatetime())
        x_sp500 = mdates.date2num(hist_sp500.index.to_pydatetime())
        # Normalize both series to 100 at the start
        y_stock = (hist_stock["Close"].values / hist_stock["Close"].values[0] - 1) * 100
        y_sp500 = (hist_sp500["Close"].values / hist_sp500["Close"].values[0] - 1) * 100

        sp_return = round(y_sp500[-1],2)
        stock_return = round(y_stock[-1],2)

        embed = discord.Embed(
            title=f"📊 {ticker} vs S&P 500 Comparison",
            description=f"Comparison of **{ticker}** and **S&P 500**",
            color=0x1f77b4
        )
        # Set footer
        embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")
        # Compare returns
        embed.add_field(name="S&P 500 Return", value=f"{sp_return}%", inline=True)
        embed.add_field(name=f"{ticker} Return", value=f"{stock_return}%", inline=True)
        buffer = build_plot([(x_stock, y_stock), (x_sp500, y_sp500)], 
        f"{ticker} vs S&P 500 - Last {period}", "Date", "Return (%)", [ticker, "S&P 500"], ["#1f77b4", "#ff7f0e"])
        file = discord.File(buffer, filename="chart.png")
        embed.set_image(url="attachment://chart.png")
        await ctx.send(file=file, embed=embed)
    except Exception as e:
        await ctx.send(f"⚠️ Error generating comparison chart: {str(e)}")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
db.close_connection()