FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    openjdk-17-jdk \
    libasound2-dev \
    libjack-jackd2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install tensorflow==2.9.1 magenta==2.1.4

# プロジェクト全体のファイルをコピー
COPY . .

# ★ここを追加：modelsフォルダをDockerの中にコピーする！
COPY models /app/models

# JavaPythonフォルダを適切な場所に配置
RUN cp -r /app/JavaPython /app/weather-music-app/

WORKDIR /app/weather-music-app

CMD ["./mvnw", "spring-boot:run"]