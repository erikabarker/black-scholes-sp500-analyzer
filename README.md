# S&P 500 Option Pricing Analyzer (Black-Scholes Model)

This is a prototype web application built with Streamlit that estimates theoretical call option prices for S&P 500 stocks using the Black-Scholes model. It fetches recent market data, calculates implied option values under standardized assumptions, and ranks stocks by the highest model-based call prices.

---

## Purpose

This tool is designed to help developers, data scientists, and finance professionals experiment with Black-Scholes modeling at scale using real market data. It supports learning and prototyping, not live investment decisions.

---

## How It Works

The application performs the following operations:

1. **Retrieves the list of S&P 500 tickers**  
   Pulls the current list from a Alpha Vantage API.

2. **Fetches adjusted close price data**  
   For each selected stock, it uses the Alpha Vantage API to retrieve the most recent 30 days of adjusted daily close prices.

3. **Calculates annualized historical volatility**  
   Volatility is computed from log returns of the adjusted close price series.

4. **Fetches the current risk-free rate**  
   The latest 1-month U.S. Treasury yield is fetched via the FRED API and used as the risk-free rate.

5. **Estimates theoretical call option values**  
   Assumes:
   - European-style call
   - At-the-money strike (K = current price)
   - 30-day time to expiration
   - Constant volatility and interest rate
   - No dividends

   The Black-Scholes formula calculates:
   - Option price
   - Delta (sensitivity to underlying)
   - Vega (sensitivity to volatility)

6. **Estimates buying power**  
   Based on user input for total trading liquidity, the tool estimates how many contracts (lots of 100 shares) the user could afford per stock.

7. **Renders results**  
   A ranked table displays the top 25 stocks by option value, including call price, volatility, delta, vega, and number of contracts affordable.

---

## API Keys Required

You must supply your own API keys by replacing the placeholders in the script:

### 1. Alpha Vantage API Key

- Used to fetch historical stock price data
- Free keys available at: https://www.alphavantage.co/support/#api-key

**Example usage in code:**
```python
ALPHA_VANTAGE_KEY = "your_alpha_vantage_api_key"
