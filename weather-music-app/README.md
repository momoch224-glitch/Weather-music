# Weather Music App

Weather Music は、天気情報をもとに音楽を自動生成するアプリです。

まずはこの URL にアクセスすれば、すぐに使い始められます。

- https://u-22-u3x4.onrender.com/

天気の状態や都市名を入力すると、その地域の天気に合わせて曲の雰囲気や進行が自動で作られます。

## 使い方

1. ブラウザで公開 URL を開く
2. 都市名を入力する
3. 生成を実行する
4. 天気に合わせた音楽が作成される

たとえば、晴れの日は明るい雰囲気、雨の日は落ち着いた雰囲気、曇りの日は中間の雰囲気として生成されます。

## ローカルで起動したい場合

### 必要環境

- Java 17
- Python 3.8 以上
- Maven または Maven Wrapper (`mvnw`)

### 起動コマンド

```bash
cd weather-music-app
./mvnw spring-boot:run
```

Windows の場合:

```bash
cd weather-music-app
mvnw.cmd spring-boot:run
```

起動後は次の URL にアクセスしてください。

```text
http://localhost:8080
```

## 生成されるもの

このアプリでは、天気情報をもとに次のような音楽要素が自動生成されます。

- 季節
- 天気の状態
- キー
- コード進行
- BPM
- MIDI / 音楽生成データ

## 注意事項

- 初回起動時には依存ライブラリの準備に時間がかかる場合があります。
- Python と Java の環境が整っている必要があります。
- 公開 URL は Render のデプロイ環境に依存するため、ローカル環境と挙動が異なる場合があります。

## 参考

- GitHub リポジトリ: https://github.com/momoch224-glitch/Weather-music
- アプリ本体: https://github.com/momoch224-glitch/Weather-music/tree/main/weather-music-app

このアプリは、天気を入力するだけで音楽が作れる体験型の仕組みです。
まずは公開 URL にアクセスして試してみてください。
