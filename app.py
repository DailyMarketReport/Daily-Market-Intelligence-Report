from flask import Flask, render_template
import yfinance as yf
import feedparser

app = Flask(__name__)

def get_market_data():
    # 國債數據
    rates = {}
    tickers = {"1Y": "^IRX", "5Y": "^FVX", "10Y": "^TNX", "30Y": "^TYX"}
    try:
        for label, t in tickers.items():
            data = yf.Ticker(t).history(period="1d")
            rates[label] = f"{data['Close'].iloc[-1]:.2f}%" if not data.empty else "N/A"
    except:
        pass

    # 中文新聞數據
    news_data = []
    try:
        feed = feedparser.parse("https://hk.finance.yahoo.com/news/rss")
        for entry in feed.entries[:6]:
            news_data.append({
                "title": entry.get('title', '無標題'),
                "link": entry.get('link', '#'),
                "time": entry.get('published', '')[17:22] if 'published' in entry else "即時"
            })
    except:
        news_data = [{"title": "新聞加載失敗", "link": "#", "time": ""}]
    
    return rates, news_data

@app.route('/')
def index():
    # 確保即使抓取失敗，變數依然存在，防止 HTML 報錯
    try:
        rates, news = get_market_data()
    except:
        rates, news = {}, []
    return render_template('index.html', rates=rates, news=news)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
