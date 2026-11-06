"""Stock-price lookup tool (Yahoo Finance via yfinance)."""
from typing import Dict, List


def get_financial_context(tickers: List[str]) -> Dict[str, str]:
    """
    Fetches the current stock price and daily change for a list of stock tickers.

    Args:
        tickers: A list of stock market tickers (e.g., ["NVDA", "MSFT"]).

    Returns:
        A dictionary mapping each ticker to a formatted string such as "$950.00 (+1.50%)".
        Invalid or missing tickers return a readable message instead of raising.
    """
    financial_data: Dict[str, str] = {}

    # Filter out placeholder / invalid tickers up front
    valid_tickers = [
        t.upper().strip() for t in tickers
        if t and t.upper().strip() not in ("N/A", "NA", "")
    ]
    if not valid_tickers:
        return {t: "No financial data" for t in tickers}

    import yfinance as yf  # imported lazily so the module loads even without network deps

    for ticker_symbol in valid_tickers:
        try:
            info = yf.Ticker(ticker_symbol).info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            change_percent = info.get("regularMarketChangePercent")

            if price is not None and change_percent is not None:
                financial_data[ticker_symbol] = f"${price:.2f} ({change_percent * 100:+.2f}%)"
            else:
                financial_data[ticker_symbol] = "Price data not available."
        except Exception:
            financial_data[ticker_symbol] = "Invalid Ticker or Data Error"

    return financial_data
