import os
import markdown
import feedparser
import yfinance as yf
from flask import Flask, render_template

app = Flask(__name__)

# 設定報告儲存目錄
REPORTS_DIR = 'reports'
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

def get_market_data():
    """獲取宏觀數據、商品報價與新聞"""
    
    # 1. 抓取美國國債收益率 (使用 yfinance 模擬)
    # 常用 Tickers: ^IRX (13週), ^FVX (5年), ^TNX (10年), ^TYX (30年)
    yield_tickers = {
        "1Y": "^IRX", 
        "5Y": "^FVX", 
        "10Y": "^TNX", 
        "30Y": "^TYX"
    }
    rates = {}
    for label, ticker in yield_tickers.items():
        try:
            data = yf.Ticker(ticker).fast_info
            rates[label] = f"{data.last_price:.2f}%"
        except:
            rates[label] = "N/A"

    # 2. 抓取商品與匯率 (依據你的最新需求)
    asset_tickers = {
        "黃金價格": "GC=F",
        "白銀價格": "SI=F",
        "BITCOIN價格": "BTC-USD",
        "英鎊/港元": "GBPHKD=X"
    }
    other_assets = {}
    for name, ticker in asset_tickers.items():
        try:
            asset = yf.Ticker(ticker).fast_info
            price = asset.last_price
            # 匯率保留四位小數，其餘兩位並加千分位
            if "英鎊" in name:
                other_assets[name] = f"{price:.4f}"
            else:
                other_assets[name] = f"{price:,.2f}"
        except:
            other_assets[name] = "N/A"

    # 3. Yahoo 財經即時快訊 (中文) - 抓取 10 則
    news_data = []
    try:
        rss_url = "https://hk.finance.yahoo.com/news/rss"
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:10]: # 嚴格取 10 則
            # 格式化時間 (擷取 HH:MM)
            time_str = entry.get('published', '')[17:22] if 'published' in entry else "即時"
            news_data.append({
                "title": entry.get('title', '無標題'),
                "link": entry.get('link', '#'),
                "time": time_str
            })
    except:
        news_data = [{"title": "新聞加載暫時失效", "link": "#", "time": "--"}]

    return rates, other_assets, news_data

def get_reports():
    """讀取 reports 資料夾下的 Markdown 檔案並轉為 HTML"""
    reports_list = []
    try:
        # 獲取所有 .md 檔案並按檔名排序 (通常檔名帶日期可實現倒序)
        files = sorted([f for f in os.listdir(REPORTS_DIR) if f.endswith('.md')], reverse=True)
        
        for filename in files:
            file_path = os.path.join(REPORTS_DIR, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                # 將 Markdown 轉成 HTML
                html_content = markdown.markdown(text, extensions=['extra', 'codehilite'])
                # 建立標題 (去除 .md 並將連字號轉空格)
                display_title = filename.replace('.md', '').replace('-', ' ').title()
                
                reports_list.append({
                    "title": display_title,
                    "content": html_content
                })
    except Exception as e:
        print(f"讀取報告出錯: {e}")
        
    return reports_list

@app.route('/')
def index():
    # 獲取所有數據
    rates, other_assets, news = get_market_data()
    # 獲取長篇分析報告
    reports = get_reports()
    
    return render_template('index.html', 
                           rates=rates, 
                           other_assets=other_assets, 
                           news=news, 
                           reports=reports)

if __name__ == '__main__':
    # 調試模式啟動
    app.run(debug=True, port=5000)
