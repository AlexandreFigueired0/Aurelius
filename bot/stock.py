import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import yfinance as yf
import matplotlib.dates as mdates
import database_service as db
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
    

    # If server has PRO plan, show advanced metrics
    server_id = ctx.message.guild.id
    plan = db.get_server_plan(server_id)

    ev = round(float(info.get("enterpriseValue", 0)), 2)
    trailing_pe = round(float(info.get("trailingPE", 0)), 2)
    forward_pe = round(float(info.get("forwardPE", 0)), 2)
    dividend_yield = round(float(info.get("dividendYield", 0)), 2)
    price_to_book = round(float(info.get("priceToBook", 0)), 2)
    beta = round(float(info.get("beta", 0)), 2)
    target_high = round(float(info.get("targetHighPrice", 0)), 2)
    target_low = round(float(info.get("targetLowPrice", 0)), 2)
    target_mean = round(float(info.get("targetMeanPrice", 0)), 2)
    recommendation = info.get("recommendationKey", "N/A")

    earnings_growth = round(float(info.get("earningsGrowth", 0)), 2) * 100
    shares_outstanding = round(float(info.get("sharesOutstanding", 0)), 2)
    revenue_growth = round(float(info.get("revenueGrowth", 0)), 2) * 100
    fcf = round(float(info.get("freeCashflow", 0)), 2)


    # --- Create an embed dashboard ---
    embed = discord.Embed(
        title=f"📊 {ticker} Key Financial Metrics",
        description=f"Key financial metrics of **{ticker}**"
    )

    pro_only = "🔒 PRO Plan Only"
    embed.add_field(name="💼 Enterprise Value (EV)", value=f"${round_large_number(ev)}" , inline=True)
    embed.add_field(name="📊 Trailing P/E", value=f"{trailing_pe}" , inline=True)
    embed.add_field(name="🔮 Forward P/E", value=f"{forward_pe}" , inline=True)
    embed.add_field(name="💰 Dividend Yield", value=f"{dividend_yield}%" , inline=True)
    embed.add_field(name="📈 Beta", value=f"{beta}" , inline=True)
    embed.add_field(name="🏦 Price to Book", value=f"{price_to_book}" , inline=True)
    embed.add_field(name="🎯 Target Price (High)", value=f"${target_high}" if plan and plan[0] == "PRO" else pro_only , inline=True)
    embed.add_field(name="🎯 Target Price (Low)", value=f"${target_low}" if plan and plan[0] == "PRO" else pro_only, inline=True)
    embed.add_field(name="🎯 Target Price (Mean)", value=f"${target_mean}" if plan and plan[0] == "PRO" else pro_only, inline=True)
    embed.add_field(name="📝 Recommendation", value=recommendation.capitalize() if plan and plan[0] == "PRO" else pro_only, inline=True)
    embed.add_field(name="📈 Earnings Growth (5Y)", value=f"{earnings_growth}" if plan and plan[0] == "PRO" else pro_only, inline=True)
    embed.add_field(name="📊 Revenue Growth (5Y)", value=f"{revenue_growth}" if plan and plan[0] == "PRO" else pro_only, inline=True)
    embed.add_field(name="💵 Free Cash Flow (FCF)", value=f"${round_large_number(fcf)}" if plan and plan[0] == "PRO" else pro_only, inline=True)

    embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")
    await ctx.send(embed=embed)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
db.close_connection()