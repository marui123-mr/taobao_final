FROM python:3-alpine
WORKDIR /app
COPY . .
RUN pip config set global.index-url http://mirrors.cloud.tencent.com/pypi/simple && \
    pip install --no-cache-dir -r requirements.txt
EXPOSE 80
CMD exec gunicorn --bind :80 --workers 1 --threads 4 app:app