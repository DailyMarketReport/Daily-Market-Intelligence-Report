# 使用最輕量的伺服器鏡像
FROM nginx:alpine

# 刪除 Nginx 預設的網頁檔案
RUN rm /usr/share/nginx/html/*

# 將你的 index.html 複製進去
COPY index.html /usr/share/nginx/html/index.html

# 讓 Nginx 監聽 8080 端口 (Cloud Run 的標準)
RUN sed -i 's/listen  80;/listen 8080;/g' /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
