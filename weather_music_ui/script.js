// config.js からAPIキーを取得
const API_KEY = CONFIG.API_KEY;

// 1. 地図の初期設定
const map = L.map('map').setView([35.6812, 139.7671], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let currentMarker = null;

// 2. マーカーを更新する共通関数
function updateMarker(lat, lon) {
    if (currentMarker) {
        map.removeLayer(currentMarker);
    }
    currentMarker = L.marker([lat, lon]).addTo(map)
        .bindPopup("天気を取得しています...☁️")
        .openPopup();
}

// 3. 地図をクリックした時の処理
map.on('click', function(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    updateMarker(lat, lon);
    getWeather(lat, lon);
});

// 4. ボタンを押した時の処理
document.getElementById("getWeatherButton").onclick = function () {
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            map.setView([lat, lon], 12); // 現在地にズーム
            updateMarker(lat, lon);
            getWeather(lat, lon);
        },
        () => {
            document.getElementById("city").textContent = "Location Error";
            document.getElementById("condition").textContent = "位置情報を取得できません";
        }
    );
};

// 5. 天気を取得して画面を更新する処理
async function getWeather(lat, lon) {
    try {
        const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric`;
        const response = await fetch(url);
        
        if (!response.ok) throw new Error("API Error");

        const data = await response.json();
        const cityName = data.name ? data.name : "不明な場所（海など）";
        
        // HTMLのカード部分を更新
        document.getElementById("city").textContent = cityName;
        document.getElementById("condition").textContent = data.weather[0].main;
        document.getElementById("temp").textContent = data.main.temp + "℃";
        document.getElementById("humidity").textContent = "Humidity: " + data.main.humidity + "%";

        // 地図のピンの吹き出しも更新
        if (currentMarker) {
            currentMarker.bindPopup(`<b>${cityName}</b><br>${data.weather[0].main} / ${data.main.temp}℃`).openPopup();
        }

    } catch (err) {
        document.getElementById("city").textContent = "Error";
        document.getElementById("condition").textContent = err.message;
        if (currentMarker) {
            currentMarker.bindPopup("取得失敗").openPopup();
        }
    }
}