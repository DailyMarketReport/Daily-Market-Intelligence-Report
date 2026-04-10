# 第一階段：使用 Nginx 鏡像
FROM nginx:alpine

# 複製 index.html 到 Nginx 預設目錄
COPY index.html /usr/share/nginx/html/index.html

# 強制 Nginx 監聽 8080 端口，並確保配置正確
RUN printf 'server {\n\
    listen 8080;\n\
    location / {\n\
        root /usr/share/nginx/html;\n\
        index index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

# 宣告 8080 端口
EXPOSE 8080

# 啟動 Nginx
CMD ["nginx", "-g", "daemon off;"]
