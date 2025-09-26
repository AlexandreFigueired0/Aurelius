
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import yfinance as yf
import matplotlib.dates as mdates
import database_service as db
from helpers import build_plot, round_large_number
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


@bot.command()
async def compare(ctx, arg1, arg2, period="1y"):
    '''PAID COMMAND. Compare historical stock data for two given ticker symbols and period (default: 1 month).'''

    # Check if server has a paid plan
    server_id = ctx.message.guild.id
    plan = db.get_server_plan(server_id)
    if not plan or plan[0] != "PRO":
        await ctx.send("❌ This command is available for PRO plan subscribers only. Please upgrade your plan to access this feature.")
        return

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
    '''PAID COMMAND. Compare historical stock data for a given ticker symbol against S&P 500 index and period (default: 1 year).'''

    # Check if server has a paid plan
    server_id = ctx.message.guild.id
    plan = db.get_server_plan(server_id)
    if not plan or plan[0] != "PRO":
        await ctx.send("❌ This command is available for PRO plan subscribers only. Please upgrade your plan to access this feature.")
        return

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