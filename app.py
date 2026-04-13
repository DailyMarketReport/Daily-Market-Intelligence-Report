import os
import markdown
import feedparser
import yfinance as yf
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# 確保報告資料夾存在
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

    # 2. 市場關鍵指標
    asset_tickers = {"黃金價格": "GC=F", "白銀價格": "SI=F", "BITCOIN價格": "BTC-USD", "英鎊/港元": "GBPHKD=X"}
    other_assets = {}
    for name, ticker in asset_tickers.items():
        try:
            price = yf.Ticker(ticker).fast_info.last_price
            other_assets[name] = f"{price:.4f}" if "HKD" in name else f"{price:,.2f}"
        except:
            other_assets[name] = "N/A"

    # 3. Yahoo 新聞
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
    
    # 同時獲取 .md 和 .pdf 檔案
    files = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith(('.md', '.pdf'))], reverse=True)
    
    for filename in files:
        display_title = filename.replace('.md', '').replace('.pdf', '').replace('-', ' ')
        file_path = os.path.join(REPORTS_DIR, filename)
        
        try:
            if filename.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    html_content = markdown.markdown(text, extensions=['extra', 'tables', 'fenced_code'])
                    reports_list.append({
                        "title": display_title,
                        "content": html_content,
                        "type": "md"
                    })
            elif filename.endswith('.pdf'):
                # PDF 僅傳遞檔案名稱，由前端 serve_report 讀取
                reports_list.append({
                    "title": display_title,
                    "filename": filename,
                    "type": "pdf"
                })
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            
    return reports_list

# 提供 PDF 檔案的路由
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
