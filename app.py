import os
import markdown
import feedparser
import yfinance as yf
from flask import Flask, render_template, json

app = Flask(__name__)

REPORTS_DIR = 'reports'
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

def get_market_data():
    # 1. 國債收益率
    yield_tickers = {"1Y": "^IRX", "5Y": "^FVX", "10Y": "^TNX", "30Y": "^TYX"}
    rates = {}
    for label, ticker in yield_tickers.items():
        try:
            rates[label] = f"{yf.Ticker(ticker).fast_info.last_price:.2f}%"
        except:
            rates[label] = "N/A"

    # 2. 市場關鍵指標 (金、銀、比特幣、匯率)
    asset_tickers = {"黃金價格": "GC=F", "白銀價格": "SI=F", "BITCOIN價格": "BTC-USD", "英鎊/港元": "GBPHKD=X"}
    other_assets = {}
    for name, ticker in asset_tickers.items():
        try:
            price = yf.Ticker(ticker).fast_info.last_price
            other_assets[name] = f"{price:.4f}" if "HKD" in name else f"{price:,.2f}"
        except:
            other_assets[name] = "N/A"

    # 3. Yahoo 新聞 (10則)
    news_data = []
    try:
        feed = feedparser.parse("https://hk.finance.yahoo.com/news/rss")
        for entry in feed.entries[:10]:
            news_data.append({
                "title": entry.get('title', '無標題'),
                "link": entry.get('link', '#'),
                "time": entry.get('published', '')[17:22]
            })
    except:
        news_data = [{"title": "新聞加載失敗", "link": "#", "time": "--"}]

    return rates, other_assets, news_data

def get_reports():
    reports_list = []
    if not os.path.exists(REPORTS_DIR): return reports_list
    
    files = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith('.md')], reverse=True)
    for filename in files:
        try:
            with open(os.path.join(REPORTS_DIR, filename), 'r', encoding='utf-8') as f:
                text = f.read()
                # 啟用擴展以支援表格與進階格式
                html_content = markdown.markdown(text, extensions=['extra', 'tables', 'fenced_code'])
                reports_list.append({
                    "title": filename.replace('.md', '').replace('-', ' '),
                    "content": html_content
                })
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    return reports_list

@app.route('/')
def index():
    rates, other_assets, news = get_market_data()
    reports = get_reports()
    return render_template('index.html', rates=rates, other_assets=other_assets, news=news, reports=reports)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
