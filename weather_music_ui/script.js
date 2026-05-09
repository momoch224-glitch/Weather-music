// config.js から取得
const API_KEY = CONFIG.API_KEY;


// ボタン取得
const button =
  document.getElementById("getWeatherButton");


// ボタン押下
button.onclick = function () {

  navigator.geolocation.getCurrentPosition(
    success,
    error
  );

};


// 成功時
function success(position) {

  const lat = position.coords.latitude;

  const lon = position.coords.longitude;

  getWeather(lat, lon);

}


// エラー時
function error() {

  document.getElementById("city").textContent =
    "Location Error";

  document.getElementById("condition").textContent =
    "位置情報を取得できません";

}


// API取得
async function getWeather(lat, lon) {

  try {

    const url =
      `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${API_KEY}&units=metric`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error("API Error");
    }

    const data = await response.json();

    updateUI(data);

  } catch (err) {

    document.getElementById("city").textContent =
      "Error";

    document.getElementById("condition").textContent =
      err.message;

  }

}


// UI更新
function updateUI(data) {

  document.getElementById("city").textContent =
    data.name;

  document.getElementById("condition").textContent =
    data.weather[0].main;

  document.getElementById("temp").textContent =
    data.main.temp + "℃";

  document.getElementById("humidity").textContent =
    "Humidity: " + data.main.humidity + "%";

}