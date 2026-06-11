FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip
# ここを 2.9.1 に固定する
RUN pip install tensorflow==2.9.1 magenta==2.1.4

COPY . .

CMD ["python", "main.py"]