import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import yfinance as yf


def build_plot( data: list , title: str, x_label: str, y_label: str, line_labels:list, line_colors: list):
    ''' Build a matplotlib plot from given data'''
    # Create chart
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(9, 4))
    index = 0

    ax.set_title(title, fontsize=14, weight="bold", color="white")
    ax.set_ylabel(y_label, fontsize=12, color="white")
    ax.set_xlabel(x_label, fontsize=12, color="white")
    y_min = min([min(y) for x,y in data])
    # y_min = min([min(v for v in y if v) for x, y in data])
    for x,y in data:
        line_color = line_colors[index]
        ax.plot(x, y, color=line_color, linewidth=2, label=line_labels[index])
        ax.fill_between(x, y, y_min, color=line_color, alpha=0.1)
        index += 1

    if len(data) > 1:
        ax.legend()
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

    return buffer

def convert_to_eur(amount):
    ''' Convert USD to EUR using yfinance exchange rate '''
    exchange_rate = yf.Ticker("USDEUR=X").fast_info['lastPrice']
    return amount * exchange_rate

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
    if not number: return 0

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