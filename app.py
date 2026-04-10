from flask import Flask, render_template
import yfinance as yf
import feedparser

app = Flask(__name__)

def get_market_data():
    # 1. 國債數據 (維持現狀)
    treasury_tickers = {
        "1Y": "^IRX",  
        "5Y": "^FVX", 
        "10Y": "^TNX", 
        "30Y": "^TYX"
    }
    rates = {}
    for label, ticker in treasury_tickers.items():
        try:
            data = yf.Ticker(ticker)
            val = data.fast_info['last_price']
            rates[label] = f"{val:.2f}%"
        except:
            rates[label] = "N/A"

    # 2. Yahoo 財經繁體中文新聞 (直接抓取中文源)
    news_data = []
    try:
        # 使用 Yahoo 財經香港的全球新聞 RSS
        rss_url = "https://hk.finance.yahoo.com/news/rss"
        feed = feedparser.parse(rss_url)
        
        # 抓取前 6 則中文新聞
        for entry in feed.entries[:6]:
            news_data.append({
                "title": entry.title,
                "link": entry.link,
                "time": entry.published[17:22] if 'published' in entry else "即時"
            })
    except:
        news_data = [{"title": "暫時無法獲取中文新聞", "link": "#", "time": ""}]

    return rates, news_data

@app.route('/')
def index():
    rates, news = get_market_data()
    return render_template('index.html', rates=rates, news=news)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
