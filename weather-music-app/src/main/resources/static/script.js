// script.js
const API_KEY = CONFIG.API_KEY;

// 1. 地図の初期設定
const map = L.map('map').setView([35.6812, 139.7671], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let currentMarker = null;

function updateMarker(lat, lon) {
    if (currentMarker) map.removeLayer(currentMarker);
    currentMarker = L.marker([lat, lon]).addTo(map)
        .bindPopup("天気を取得しています...☁️")
        .openPopup();
}

// 地図をクリックした時の処理
map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    updateMarker(lat, lon);
    getWeather(lat, lon);
});

// ボタンを押した時の処理
document.getElementById("getWeatherButton").onclick = function () {
    document.getElementById("status-text").textContent = "位置情報を取得中...";
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            map.setView([lat, lon], 12);
            updateMarker(lat, lon);
            getWeather(lat, lon);
        },
        () => {
            document.getElementById("status-text").textContent = "位置情報を取得できません";
        }
    );
};

// 天気を取得して画面を更新する処理
async function getWeather(lat, lon) {
    const loadingOverlay = document.getElementById("loading-overlay");

    try {
        // 🌟 処理開始：ロード画面を表示する
        loadingOverlay.classList.remove("hidden");
        loadingOverlay.classList.add("flex");

        // --- 1. 天気情報の取得 ---
        const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric`;
        const response = await fetch(url);
        
        if (!response.ok) throw new Error("API Error");

        const data = await response.json();
        const cityName = data.name ? data.name : "不明な場所";
        
        UI.updateWeatherUI(data, cityName);
        document.getElementById("status-text").textContent = "音楽を生成中... (バックエンドと通信中)";

// --- 2. 待ち時間の表示設定（濁すバージョン） ---
        const loadingText = document.getElementById("loading-text");
        // 最初に目安を伝えておく（お茶マークなどでリラックス効果を狙う）
        loadingText.textContent = "音楽を生成中... (約3〜5分かかります☕)";

        // 進行状況に合わせてメッセージを変える（ユーザーを飽きさせない工夫）
        const messages = [
            "天気のデータを解析しています...",
            "メロディを構想中...",
            "和音を調整しています...",
            "音色を重ねています...",
            "こだわりのアレンジに仕上げ中...",
            "あともう少しで完成します！"
        ];
        let messageIndex = 0;

        // 30秒（30000ミリ秒）ごとにメッセージを切り替える
        const countdownTimer = setInterval(() => {
            loadingText.textContent = messages[messageIndex];
            messageIndex++;
            
            // 用意したメッセージを全て表示しきったら最後のもので固定する
            if (messageIndex >= messages.length) {
                messageIndex = messages.length - 1; 
            }
        }, 30000);

        // --- 3. 音楽生成（Spring Boot APIとの通信） ---
        try {
            const apiResponse = await fetch("http://localhost:8080/generate", {
                method: "POST", // データを送るためのPOSTメソッド
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data) // 天気データをJSON形式にして送信
            });

            const resultText = await apiResponse.text();
            console.log("Spring Bootからの返答:", resultText);

            // プレイヤーの音源をセット（ブラウザのキャッシュ対策で末尾に時間を付ける）
            player.src = "final_arranged.mid?t=" + new Date().getTime();

            document.getElementById("status-text").textContent = "音楽の生成が完了しました！";

            if (currentMarker) {
                currentMarker.bindPopup(`<b>${cityName}</b><br>${data.weather[0].main} / ${Math.round(data.main.temp)}℃`).openPopup();
            }

        } finally {
            // 通信が完了したら（成功・失敗問わず）タイマーを完全に止める
            clearInterval(countdownTimer);
            loadingText.textContent = "Generating Music..."; // テキストを初期状態に戻す
        }

    } catch (err) {
        console.error("処理全体のエラー:", err);
        document.getElementById("status-text").textContent = "処理に失敗しました";
    } finally {
        // 🌟 処理完了：成功しても失敗してもロード画面を消す
        loadingOverlay.classList.add("hidden");
        loadingOverlay.classList.remove("flex");
    }
}

// ==========================================
// ボタンとプログレスバーの連動処理
// ==========================================

const player = document.getElementById("hidden-player");
const playBtn = document.getElementById("play-btn");
const progressBar = document.getElementById("progress-bar"); // バーの要素を取得

const playIcon = `<svg class="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>`;
const stopIcon = `<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h12v12H6z"/></svg>`;

let progressInterval; // タイマー用の変数

// プログレスバーを更新する関数
function updateProgress() {
    // Magentaのプレイヤーから総再生時間と現在の再生時間を取得
    const totalTime = player.duration;
    const currentTime = player.currentTime;

    if (totalTime > 0) {
        // パーセンテージを計算（最大100%）
        const percentage = (currentTime / totalTime) * 100;
        // バーの幅(width)を更新
        progressBar.style.width = percentage + "%";
    }

    // 最後まで再生し終わったら停止状態に戻す
    if (currentTime >= totalTime && totalTime > 0) {
        clearInterval(progressInterval);
        playBtn.innerHTML = playIcon;
        progressBar.style.width = "100%"; // 念のため100%で止める
    }
}

// 再生ボタンを押した時の処理
playBtn.onclick = function () {
    if (player.playing) {
        // 再生中なら停止
        player.stop();
        playBtn.innerHTML = playIcon;
        // タイマーを止める
        clearInterval(progressInterval);
    } else {
        // 停止中なら再生
        player.start();
        playBtn.innerHTML = stopIcon;
        // 100ミリ秒（0.1秒）ごとにバーを更新するタイマーを開始
        progressInterval = setInterval(updateProgress, 100);
    }
};

// ダウンロードボタンを押した時の処理
document.getElementById("download-btn").onclick = function () {
    const midiUrl = player.src;
    
    if (!midiUrl) {
        alert("まだ音楽が生成されていません！");
        return;
    }

    const a = document.createElement("a");
    a.href = midiUrl;
    a.download = "weather_music.mid";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
};