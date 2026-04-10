# 使用 Python 官方輕量鏡像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製所有檔案到容器中
COPY . .

# 安裝必要的 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 讓 Flask 知道在哪個 Port 運行
ENV PORT 8080

# 啟動命令
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
