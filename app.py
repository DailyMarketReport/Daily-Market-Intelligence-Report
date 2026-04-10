from flask import Flask, render_template
import yfinance as yf
import pandas as pd

app = Flask(__name__)

def get_real_market_data():
    # 1. 抓取美國國債利率 (真實數據)
    # ^IRX: 13週(約3個月), ^FVX: 5年, ^TNX: 10年, ^TYX: 30年
    treasury_tickers = {
        "3M": "^IRX", 
        "5Y": "^FVX", 
        "10Y": "^TNX"
    }
    rates = {}
    for label, ticker in treasury_tickers.items():
        try:
            data = yf.Ticker(ticker)
            current_yield = data.fast_info['last_price']
            rates[label] = f"{current_yield:.2f}%"
        except:
            rates[label] = "N/A"

    # 2. 抓取 Mega 7 股價與漲跌幅
    mega7_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
    mega7_data = []
    try:
        stocks = yf.download(mega7_tickers, period="1d", group_by='ticker')
        for ticker in mega7_tickers:
            last_price = stocks[ticker]['Close'].iloc[-1]
            prev_price = stocks[ticker]['Open'].iloc[-1]
            change = ((last_price - prev_price) / prev_price) * 100
            mega7_data.append({
                "ticker": ticker, 
                "price": f"${last_price:.2f}", 
                "change": f"{change:+.2f}%"
            })
    except:
        pass

    return rates, mega7_data

@app.route('/')
def index():
    rates, mega7 = get_real_market_data()
    return render_template('index.html', rates=rates, mega7=mega7)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
