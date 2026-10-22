# Weather Music App

Weather Music は、天気情報から音楽を自動生成するアプリケーションです。
都市名を入力すると、その都市の天気情報を取得し、季節・天気・湿度・風速の変化量をもとに MIDI 生成や音楽構成の出力を行います。

## 1. 起動手順

### 必要環境

- Java 17
- Maven または Maven Wrapper (`mvnw`)
- Python 3.8 以上
- ffmpeg（MIDI/音声処理で利用される場合があります）
- 依存ライブラリ: `requirements.txt` またはプロジェクトの Python 周りの環境

### ローカル起動

リポジトリのルートで次を実行します。

```bash
cd weather-music-app
./mvnw spring-boot:run
```

Windows の場合は次のように実行してください。

```bash
cd weather-music-app
mvnw.cmd spring-boot:run
```

### Docker で起動する場合

リポジトリのルートで以下を実行します。

```bash
docker build -t weather-music-app .
docker run -p 8080:8080 weather-music-app
```

このプロジェクトのルートにある `Dockerfile` では、アプリ起動時に `./mvnw spring-boot:run` が実行される構成になっています。

## 2. アクセスURL

ローカル開発環境で起動した場合:

- http://localhost:8080

公開デプロイ済みの URL（Render 等）を利用する場合:

- https://u-22-u3x4.onrender.com/

※ Render などのクラウド環境では、ポート番号や起動コマンドがデプロイ環境に合わせて設定されている必要があります。ローカルでは基本的に `http://localhost:8080` でアクセスできます。

## 3. 使い方

### 基本フロー

1. ブラウザで `http://localhost:8080` にアクセスする
2. 画面で都市名を入力する
3. アプリが天気情報を取得する
4. 季節・天気・気圧・湿度・風速変化量をもとに、音楽のキーやコード進行を生成する
5. MIDI や音楽ファイルの生成結果を確認する

### 実行例

```bash
cd weather-music-app
./mvnw spring-boot:run
```

その後、ブラウザで以下を開いてください。

```text
http://localhost:8080
```

### 生成されるファイル

アプリ実行中に次のような出力が生成される可能性があります。

- `chords.json`
- `final.mid`
- `output_melody.mid`
- `weather-music-app` 配下の生成物

## 4. 注意事項

- このアプリは天気APIと Python ベースの音楽生成処理を利用するため、ネットワーク接続と依存環境が必要です。
- Python のライブラリや TensorFlow / Magenta 系の依存が重いため、初回起動時には時間がかかる場合があります。
- 環境変数や Render の設定が未整備のままだと、公開URLでの起動に失敗することがあります。

## 5. 参考

- リポジトリ本体: https://github.com/momoch224-glitch/Weather-music
- アプリ本体ディレクトリ: https://github.com/momoch224-glitch/Weather-music/tree/main/weather-music-app

必要であれば次に、Render 向けの `start.sh` や `Procfile` まで含めた「本番公開用の設定」まで整えます。
