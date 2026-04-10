from flask import Flask, render_template
import yfinance as yf
import feedparser

app = Flask(__name__)

def get_market_data():
    # 1. 精確國債數據
    treasury_tickers = {
        "1Y": "^IRX", 
        "5Y": "^FVX", 
        "10Y": "^TNX", 
        "30Y": "^TYX"
    }
    rates = {}
    for label, ticker in treasury_tickers.items():
        try:
            # 獲取最新價格 (Yield %)
            data = yf.Ticker(ticker)
            val = data.fast_info['last_price']
            rates[label] = f"{val:.2f}%"
        except:
            rates[label] = "N/A"

    # 2. Yahoo Finance 美股新聞 (透過 RSS 抓取，不會被擋)
    news_data = []
    try:
        # 這是 Yahoo Finance 官方的 RSS 源
        rss_url = "https://finance.yahoo.com/news/rss"
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:6]: # 抓前 6 條
            news_data.append({
                "title": entry.title,
                "link": entry.link,
                "time": entry.published[17:22] # 只取時間部分
            })
    except:
        news_data = [{"title": "新聞抓取暫時不可用", "link": "#", "time": ""}]

    return rates, news_data

@app.route('/')
def index():
    rates, news = get_market_data()
    return render_template('index.html', rates=rates, news=news)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
