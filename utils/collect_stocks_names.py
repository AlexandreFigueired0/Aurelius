import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SEC_URL = "https://www.sec.gov/files/company_tickers.json"

def _user_agent() -> str:
    # SEC requests a descriptive UA with contact info
    return os.environ.get("SEC_USER_AGENT", "Aurelius/1.0 (contact: email@example.com)")

def fetch_sec_company_tickers() -> dict:
    req = Request(
        SEC_URL,
        headers={
            "User-Agent": _user_agent(),
            "Accept": "application/json",
            "Connection": "keep-alive",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            if resp.status != 200:
                raise HTTPError(SEC_URL, resp.status, "Bad response", resp.headers, None)
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, HTTPError) as e:
        raise RuntimeError(f"Failed to fetch SEC tickers: {e}") from e

    return data

def build_ticker_name_map(sec_payload: dict) -> dict[str, str]:
    # Payload is a dict keyed by numeric strings: {"0": {"ticker": "AAPL", "title": "Apple Inc.", ...}, ...}
    mapping: dict[str, str] = {}
    for entry in sec_payload.values():
        t = (entry.get("ticker") or "").strip().upper()
        name = (entry.get("title") or "").strip()
        if t and name:
            mapping[t] = name
    return mapping


def get_ticker_name_dict() -> dict[str, str]:
    payload = fetch_sec_company_tickers()
    return build_ticker_name_map(payload)

if __name__ == "__main__":
    mapping = get_ticker_name_dict()
    print(f"Built mapping: {len(mapping)} tickers")
    # Example: print a few
    for k in ("AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NET", "^GSPC"):
        if k in mapping:
            print(f"{k}: {mapping[k]}")
    print(len(mapping))