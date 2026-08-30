// script.js

// 🌟修正ポイント1：要素の準備（playerなど）を一番上に移動して、いつでも使えるようにしました！
const player = document.getElementById("hidden-player");
const playBtn = document.getElementById("play-btn");
const progressBar = document.getElementById("progress-bar"); 
const playIcon = `<svg class="w-6 h-6 ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>`;
const stopIcon = `<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h12v12H6z"/></svg>`;
let progressInterval;

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

// 現在地ボタンを押した時の処理
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

// 🌟修正ポイント2：手動入力ボタン（亡霊）の処理をまるごと削除しました！

// 天気を取得して画面を更新する処理
async function getWeather(lat, lon) {
    const loadingOverlay = document.getElementById("loading-overlay");

    try {
        loadingOverlay.classList.remove("hidden");
        loadingOverlay.classList.add("flex");

        // --- 1. 天気情報の取得 ---
// 例
const url = `http://localhost:8080/api/weather?lat=${lat}&lon=${lon}`;        const response = await fetch(url);        
        if (!response.ok) throw new Error("API Error");

        const data = await response.json();
        const cityName = data.name ? data.name : "不明な場所";
        
        UI.updateWeatherUI(data, cityName);
        document.getElementById("status-text").textContent = "音楽を生成中... (バックエンドと通信中)";

        // --- 2. 待ち時間の表示設定 ---
        const loadingText = document.getElementById("loading-text");
        loadingText.textContent = "音楽を生成中... (約30〜50分かかります☕)";

        const messages = [
            "天気のデータを解析しています...",
            "メロディを構想中...",
            "和音を調整しています...",
            "音色を重ねています...",
            "こだわりのアレンジに仕上げ中...",
            "あともう少しで完成します！"
        ];
        let messageIndex = 0;

        const countdownTimer = setInterval(() => {
            loadingText.textContent = messages[messageIndex];
            messageIndex++;
            if (messageIndex >= messages.length) {
                messageIndex = messages.length - 1; 
            }
        }, 30000);

// --- 3. 音楽生成（Spring Boot APIとの通信） ---
        try {
            // ① まず「注文」をして、受付番号（taskId）をもらう
            const apiResponse = await fetch("/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ location: cityName })
            });

            if (!apiResponse.ok) {
                throw new Error("サーバーエラー");
            }

            const initData = await apiResponse.json();
            const taskId = initData.taskId;
            console.log("受付番号をもらいました:", taskId);

            // ② 定期的に「できましたか？」と確認する（ポーリング処理）
            const checkInterval = setInterval(async () => {
                try {
                    const statusRes = await fetch(`/api/status?taskId=${taskId}`);
                    const statusData = await statusRes.json();
                    console.log("現在の状況:", statusData.status);

                    if (statusData.status === "COMPLETED") {
                        // 完了した時の処理
                        clearInterval(checkInterval); // 確認作業をストップ
                        clearInterval(countdownTimer); // メッセージ切り替えもストップ
                        
                        // 音源をセット
                        player.src = "final_arranged.mid?t=" + new Date().getTime();
                        document.getElementById("status-text").textContent = "音楽の生成が完了しました！";
                        
                        if (currentMarker) {
                            currentMarker.bindPopup(`<b>${cityName}</b><br>${data.weather[0].main} / ${Math.round(data.main.temp)}℃`).openPopup();
                        }

                        // ローディング画面をここで非表示にする
                        loadingOverlay.classList.add("hidden");
                        loadingOverlay.classList.remove("flex");
                        
                    } else if (statusData.status === "ERROR") {
                        // エラーが起きた時の処理
                        clearInterval(checkInterval);
                        clearInterval(countdownTimer);
                        throw new Error("生成中にエラーが発生しました。");
                    }
                    // "PROCESSING"（処理中）の場合は何もしないで待つ（30秒後にまた確認）

                } catch (err) {
                    console.error("確認中にエラー:", err);
                }
            }, 30000); // 30000ミリ秒（30秒）ごとに実行

        } catch (err) {
            console.error("処理全体のエラー:", err);
            document.getElementById("status-text").textContent = "処理に失敗しました";
            loadingOverlay.classList.add("hidden");
            loadingOverlay.classList.remove("flex");
        }
// ==========================================
// ボタンとプログレスバーの連動処理
// ==========================================

function updateProgress() {
    const totalTime = player.duration;
    const currentTime = player.currentTime;

    if (totalTime > 0) {
        const percentage = (currentTime / totalTime) * 100;
        progressBar.style.width = percentage + "%";
    }

    if (currentTime >= totalTime && totalTime > 0) {
        clearInterval(progressInterval);
        playBtn.innerHTML = playIcon;
        progressBar.style.width = "100%"; 
    }
}

playBtn.onclick = function () {
    if (player.playing) {
        player.stop();
        playBtn.innerHTML = playIcon;
        clearInterval(progressInterval);
    } else {
        player.start();
        playBtn.innerHTML = stopIcon;
        progressInterval = setInterval(updateProgress, 100);
    }
};

document.getElementById("download-btn").onclick = function () {
    const midiUrl = player.src;
    
    if (!midiUrl || midiUrl.includes("dummy")) {
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