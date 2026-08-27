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

COPY . .

# ★ここを追加：実際のプログラムが入っているフォルダに移動する
WORKDIR /app/weather-music-app

# 最後に司令塔であるJava(Spring Boot)を起動
CMD ["./mvnw", "spring-boot:run"]