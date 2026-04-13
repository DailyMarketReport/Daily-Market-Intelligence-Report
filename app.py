import os
import markdown
import feedparser
import yfinance as yf
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

REPORTS_DIR = 'reports'
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

def get_market_data():
    # 國債數據
    yield_tickers = {"1Y": "^IRX", "5Y": "^FVX", "10Y": "^TNX", "30Y": "^TYX"}
    rates = {l: f"{yf.Ticker(t).fast_info.last_price:.2f}%" for l, t in yield_tickers.items()}
    
    # 關鍵指標
    asset_tickers = {"黃金價格": "GC=F", "白銀價格": "SI=F", "BITCOIN": "BTC-USD", "英鎊/港元": "GBPHKD=X"}
    other_assets = {n: (f"{yf.Ticker(t).fast_info.last_price:.4f}" if "HKD" in n else f"{yf.Ticker(t).fast_info.last_price:,.2f}") for n, t in asset_tickers.items()}
    
    # Yahoo 新聞
    news_data = []
    try:
        feed = feedparser.parse("https://hk.finance.yahoo.com/news/rss")
        for entry in feed.entries[:10]:
            news_data.append({"title": entry.get('title'), "link": entry.get('link'), "time": entry.get('published')[17:22]})
    except: news_data = []
    
    return rates, other_assets, news_data

def get_reports():
    reports_list = []
    if not os.path.exists(REPORTS_DIR): return reports_list
    files = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith(('.md', '.pdf'))], reverse=True)
    for filename in files:
        display_title = filename.replace('.md', '').replace('.pdf', '').replace('-', ' ')
        if filename.endswith('.md'):
            with open(os.path.join(REPORTS_DIR, filename), 'r', encoding='utf-8') as f:
                html = markdown.markdown(f.read(), extensions=['extra', 'tables'])
                reports_list.append({"title": display_title, "content": html, "type": "md"})
        else:
            reports_list.append({"title": display_title, "filename": filename, "type": "pdf"})
    return reports_list

@app.route('/reports/<path:filename>')
def serve_report(filename):
    return send_from_directory(REPORTS_DIR, filename)

@app.route('/')
def index():
    rates, other_assets, news = get_market_data()
    reports = get_reports()
    return render_template('index.html', rates=rates, other_assets=other_assets, news=news, reports=reports)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
