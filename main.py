import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import yfinance as yf
import pandas as pd

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
    if message.author == bot.user: return # Do not answer yourselfj

    
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
    await ctx.send(f"Current stock information for **{arg}**\n💵**Price**: ${price}\n📈**Change**: {percent_change}%\n🏦**Market Cap**: {market_cap}")

    # Create an embed dashboard
    embed = discord.Embed(
        title=f"📊 {arg.upper()} Stock Dashboard",
        description=f"Live market snapshot for **{arg.upper()}**",
        color=discord.Color.green() if percent_change and percent_change >= 0 else discord.Color.red()
    )
    
    if price:
        embed.add_field(name="💵 Price", value=f"{price:.2f} {currency}", inline=True)

    embed.set_footer(text="Data provided by Yahoo Finance (yfinance)")
    
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
    if 'longBusinessSummary' in info:
        description = info['longBusinessSummary']
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        company_oficcers = info.get('companyOfficers', 'N/A')

        for officer in company_oficcers:
            if "ceo" in officer.get('title', '').lower() or "chief executive officer" in officer.get('title', '').lower():
                ceo = officer.get('name', 'N/A')
                break

        await ctx.send(f"Company information for **{arg}**\n\n{arg}\n\n**Description**: {description}\n\n**Sector**: {sector}\n\n**Industry**: {industry}\n\n👔**CEO**: {ceo}")
    else:
        await ctx.send(f"Could not retrieve data for ticker: {arg}")
    



bot.run(token, log_handler=handler, log_level=logging.DEBUG) 