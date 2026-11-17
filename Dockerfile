# 使用带完整 C 库的 slim 镜像，防止 pandas 和 sklearn 编译失败
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装（加了 --no-cache-dir 减小体积）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制所有代码
COPY . .

# 暴露 8080 端口
EXPOSE 8080

# 使用 gunicorn 启动 Flask 应用（app:app 代表 app.py 里的 app 对象）
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "4", "app:app"]