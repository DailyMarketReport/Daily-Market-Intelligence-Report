from flask import Flask, render_template
import yfinance as yf
import feedparser

app = Flask(__name__)

def get_market_data():
    # 1. 國債數據捕捉
    rates = {}
    treasury_tickers = {"1Y": "^IRX", "2Y": "2Y=F", "5Y": "^FVX", "10Y": "^TNX", "30Y": "^TYX"}
    
    try:
        for label, ticker in treasury_tickers.items():
            try:
                data = yf.Ticker(ticker)
                # 使用 history 獲取最新價格，比 fast_info 在雲端更穩定
                hist = data.history(period="1d")
                if not hist.empty:
                    val = hist['Close'].iloc[-1]
                    rates[label] = f"{val:.2f}%"
                else:
                    rates[label] = "N/A"
            except:
                rates[label] = "N/A"
    except Exception as e:
        print(f"Treasury Error: {e}")

    # 2. Yahoo 財經繁體中文新聞捕捉 (增加防錯機制)
    news_data = []
    try:
        rss_url = "https://hk.finance.yahoo.com/news/rss"
        feed = feedparser.parse(rss_url)
        
        # 檢查 feed 是否有內容
        if feed.entries:
            for entry in feed.entries[:6]:
                news_data.append({
                    "title": entry.get('title', '無標題'),
                    "link": entry.get('link', '#'),
                    "time": entry.get('published', '')[17:22] if 'published' in entry else "即時"
                })
        else:
            news_data = [{"title": "暫時無最新中文新聞", "link": "#", "time": ""}]
    except Exception as e:
        print(f"News Error: {e}")
        news_data = [{"title": "新聞加載失敗，請稍後再試", "link": "#", "time": ""}]

    return rates, news_data

@app.route('/')
def index():
    try:
        rates, news = get_market_data()
        return render_template('index.html', rates=rates, news=news)
    except Exception as e:
        # 如果真的大當機，顯示最簡單的錯誤訊息在網頁上
        return f"應用程式發生內部錯誤: {str(e)}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
