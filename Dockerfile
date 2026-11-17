# 使用带完整 C 库的 slim 镜像，防止 pandas 和 sklearn 编译失败
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 设置腾讯云 pip 镜像源并安装依赖
RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple && \
    pip install --no-cache-dir -r requirements.txt

# 复制所有代码和数据文件
COPY . .

# 暴露 8080 端口
EXPOSE 8080

# 使用 gunicorn 启动 Flask 应用
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "app:app"]