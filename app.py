from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)

# 模擬瀏覽器，防止被網站擋掉
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_market_data():
    # 1. 抓取 Finviz 5則新聞
    news_list = []
    try:
        url = "https://finviz.com/news.ashx"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Finviz 的新聞通常在 class 為 news-link-container 的表格中
        news_rows = soup.select('.news-link-container')[:5]
        for row in news_rows:
            title = row.select_one('.nn-tab-link').text
            link = row.select_one('.nn-tab-link')['href']
            # 注意：Finviz 原生不一定提供 Ticker，這裡先抓標題與時間
            news_list.append({"title": title, "link": link, "time": datetime.datetime.now().strftime("%H:%M")})
    except Exception as e:
        news_list = [{"title": f"新聞抓取失敗: {str(e)}", "link": "#", "time": "Error"}]

    # 2. 抓取美國國債利率 (從 CNBC 抓取較穩定)
    rates = {}
    try:
        url = "https://www.cnbc.com/quotes/US10Y" # 示意
        # 這裡我們用一個模擬數據，因為國債利率通常需要解析 JS 或專門 API
        # 實務上建議使用專門的財經 API (如 Yahoo Finance)
        rates = {"1Y": "4.85%", "2Y": "4.62%", "10Y": "4.21%"} 
    except:
        rates = {"1Y": "N/A", "2Y": "N/A", "10Y": "N/A"}

    return news_list, rates

@app.route('/')
def index():
    news, rates = get_market_data()
    return render_template('index.html', news=news, rates=rates)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
