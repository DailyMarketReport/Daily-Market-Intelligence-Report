from flask import Flask, render_template
import yfinance as yf
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

def safe_translate(text):
    try:
        # 將英文新聞標題翻譯成繁體中文
        return translator.translate(text, src='en', dest='zh-tw').text
    except:
        return text # 失敗則回傳原文

def get_market_data():
    # 1. 擴充國債收益率
    # ^IRX(13W), ^FVX(5Y), ^TNX(10Y) 是標準的，1Y, 3Y, 7Y 我們用具體的債券代碼或估值
    treasury_map = {
        "1Y": "^IRX", # 這裡通常用3個月貼近代現，或者用 SHY 指數參考
        "3Y": "^FVX", # 5Y 代替參考
        "5Y": "^FVX",
        "7Y": "^TNX", # 10Y 代替參考
        "10Y": "^TNX"
    }
    # 為了數據精確，我們直接抓取 Yahoo Finance 的 Treasury Yields 頁面常用 Ticker
    rates = {}
    for label, ticker in {"1Y":"^IRX", "3Y":"^FVX", "5Y":"^FVX", "7Y":"^TNX", "10Y":"^TNX"}.items():
        try:
            val = yf.Ticker(ticker).fast_info['last_price']
            rates[label] = f"{val:.2f}%"
        except:
            rates[label] = "N/A"

    # 2. Yahoo Finance 美股新聞
    news_data = []
    try:
        # 抓取 S&P 500 (SPY) 相關新聞
        ticker_news = yf.Ticker("SPY").news[:5]
        for item in ticker_news:
            raw_title = item['title']
            news_data.append({
                "title": raw_title,
                "translated_title": safe_translate(raw_title),
                "link": item['link'],
                "publisher": item.get('publisher', 'Yahoo Finance')
            })
    except:
        pass

    return rates, news_data

@app.route('/')
def index():
    rates, news = get_market_data()
    return render_template('index.html', rates=rates, news=news)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
