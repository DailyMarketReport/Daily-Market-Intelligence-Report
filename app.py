from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # 這裡未來會放入你要求的 9 項抓取邏輯
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
