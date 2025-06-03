import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from math import log, sqrt, exp
from scipy.stats import norm

# ------------------------------
# API KEYS (Provided)
# ------------------------------
ALPHA_VANTAGE_KEY = "Your KEY Here"
FRED_API_KEY = "Your KEY Here"

# ------------------------------
# Black-Scholes Model Functions
# ------------------------------
def black_scholes_call(S, K, T, r, sigma):
    """
    Calculates the Black-Scholes European Call Option price.
    Parameters:
        S (float): Current stock price
        K (float): Strike price (assumed ATM = S)
        T (float): Time to expiration in years
        r (float): Risk-free interest rate
        sigma (float): Annualized volatility
    Returns:
        call_price (float): Theoretical price of the call option
    """
    d1 = (log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    call_price = S * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
    return call_price, norm.cdf(d1), S * norm.pdf(d1) * sqrt(T)  # Return also delta and vega

# ------------------------------
# Fetch Risk-Free Rate from FRED
# ------------------------------
def fetch_risk_free_rate():
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS1MO&api_key={FRED_API_KEY}&file_type=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latest = float(data['observations'][-1]['value']) / 100  # Convert to decimal
        return latest
    else:
        st.warning("Failed to fetch risk-free rate from FRED API.")
        return 0.05  # Default fallback

# ------------------------------
# Fetch Historical Prices (Alpha Vantage)
# ------------------------------
def fetch_price_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=compact&apikey={ALPHA_VANTAGE_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        try:
            df = pd.DataFrame.from_dict(json_data['Time Series (Daily)'], orient='index').astype(float)
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            df = df[['5. adjusted close']].rename(columns={'5. adjusted close': 'adj_close'})
            return df
        except KeyError:
            return None
    return None

# ------------------------------
# Calculate Historical Volatility
# ------------------------------
def calculate_volatility(df):
    df['log_return'] = np.log(df['adj_close'] / df['adj_close'].shift(1))
    sigma = df['log_return'].std() * np.sqrt(252)  # Annualize
    return sigma

# ------------------------------
# Load S&P 500 Tickers (Static CSV or Online)
# ------------------------------
def load_sp500_tickers():
    # Static fallback list (use local CSV or hardcoded list)
    url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
    df = pd.read_csv(url)
    return df['Symbol'].tolist(), df

# ------------------------------
# Main App Logic
# ------------------------------
def main():
    st.title("Black-Scholes Analysis for S&P 500")
    st.markdown("""
    This tool calculates theoretical Black-Scholes call option values for S&P 500 stocks
    using a standardized 30-day ATM assumption and ranks the top 25 based on model value.
    """)

    tickers, full_df = load_sp500_tickers()
    selected_count = st.sidebar.slider("Number of stocks to analyze", 25, 150, 50)
    user_liquidity = st.sidebar.number_input("Enter your available trading liquidity ($)", min_value=100.0, value=1000.0, step=100.0)

    risk_free_rate = fetch_risk_free_rate()
    T = 30 / 365  # 30-day option in years

    results = []
    progress = st.progress(0)

    for i, ticker in enumerate(tickers[:selected_count]):
        df = fetch_price_data(ticker)
        time.sleep(0.8)  # Respect API rate limit

        if df is not None and len(df) >= 30:
            S = df['adj_close'].iloc[-1]
            sigma = calculate_volatility(df)
            call_price, delta, vega = black_scholes_call(S, S, T, risk_free_rate, sigma)

            affordable_contracts = int(user_liquidity // (call_price * 100)) if call_price > 0 else 0

            results.append({
                'Ticker': ticker,
                'Price': round(S, 2),
                'Volatility': round(sigma, 4),
                'Call Price': round(call_price, 2),
                'Delta': round(delta, 4),
                'Vega': round(vega, 4),
                'Contracts You Can Afford': affordable_contracts
            })

        progress.progress((i + 1) / selected_count)

    st.success("Calculation Complete")

    if results:
        results_df = pd.DataFrame(results)
        top_25 = results_df.sort_values(by='Call Price', ascending=False).head(25)

        st.subheader("Top 25 by Black-Scholes Call Price")
        st.dataframe(top_25)

        st.markdown("""
        **Note**: Assumes ATM strike price and 30-day expiration.
        Volatility is based on last 30 trading days of adjusted close prices.
        You entered $%.2f in liquidity, and contract affordability is based on that (1 contract = 100 shares).
        """ % user_liquidity)

if __name__ == "__main__":
    main()
