
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QHBoxLayout, QComboBox, QScrollArea
)
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

from weather_logic import (
    fetch_weather, fetch_forecast, get_weather_emoji,
    speak_text, listen_for_city
)

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌦 Weather App")
        self.setGeometry(300, 200, 420, 600)
        self.setStyleSheet("background-color: #ffffff;")
        self.unit = "metric"

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)


        self.title_label = QLabel("☁️ Weather Forecast App")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)


        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("🔍 Enter a city name")
        self.city_input.setFont(QFont("Segoe UI", 14))
        self.city_input.setStyleSheet("padding: 8px; border-radius: 8px; border: 1px solid #ccc;")
        self.layout.addWidget(self.city_input)


        self.unit_toggle = QComboBox()
        self.unit_toggle.addItems(["Celsius", "Fahrenheit"])
        self.unit_toggle.setStyleSheet("padding: 6px; font-size: 14px;")
        self.unit_toggle.currentIndexChanged.connect(self.change_unit)
        self.layout.addWidget(self.unit_toggle)


        button_layout = QHBoxLayout()
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.setStyleSheet("padding: 8px; font-size: 14px;")
        self.search_btn.clicked.connect(self.get_weather)

        self.voice_btn = QPushButton("🎤 Voice")
        self.voice_btn.setStyleSheet("padding: 8px; font-size: 14px;")
        self.voice_btn.clicked.connect(self.voice_search)

        button_layout.addWidget(self.search_btn)
        button_layout.addWidget(self.voice_btn)
        self.layout.addLayout(button_layout)


        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Segoe UI", 14))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("margin-top: 10px;")
        self.layout.addWidget(self.result_label)


        self.forecast_scroll = QScrollArea()
        self.forecast_scroll.setWidgetResizable(True)

        self.forecast_container = QWidget()
        self.forecast_layout = QVBoxLayout()
        self.forecast_container.setLayout(self.forecast_layout)

        self.forecast_scroll.setWidget(self.forecast_container)
        self.layout.addWidget(self.forecast_scroll)

    def change_unit(self):
        self.unit = "metric" if self.unit_toggle.currentText() == "Celsius" else "imperial"

    def get_weather(self):
        city = self.city_input.text()
        if not city:
            QMessageBox.warning(self, "Missing City", "Please enter a city.")
            return

        current = fetch_weather(city, self.unit)
        forecast = fetch_forecast(city, self.unit)

        if current.get("cod") != 200:
            self.result_label.setText("❌ City not found.")
            return

        temp = current["main"]["temp"]
        desc = current["weather"][0]["description"].title()
        emoji = get_weather_emoji(current["weather"][0]["id"])
        unit = "°C" if self.unit == "metric" else "°F"
        weather_text = f"{emoji} <b>{desc}</b><br><br>🌡 Temperature: {temp}{unit}"
        self.result_label.setText(weather_text)


        speak_text(f"The weather in {city} is {desc} with {temp} degrees.")


        self.display_forecast(forecast)

    def display_forecast(self, data):

        for i in reversed(range(self.forecast_layout.count())):
            self.forecast_layout.itemAt(i).widget().deleteLater()

        for entry in data.get("list", []):
            dt_txt = entry["dt_txt"]
            temp = entry["main"]["temp"]
            desc = entry["weather"][0]["description"].title()
            icon_code = entry["weather"][0]["icon"]
            wind_speed = entry["wind"]["speed"]
            humidity = entry["main"]["humidity"]
            pressure = entry["main"]["pressure"]

            unit = "°C" if self.unit == "metric" else "°F"
            speed_unit = "m/s" if self.unit == "metric" else "mph"

            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"


            try:
                response = requests.get(icon_url)
                pixmap = QPixmap()
                pixmap.loadFromData(BytesIO(response.content).read())
            except:
                pixmap = QPixmap()


            forecast_item = QWidget()
            layout = QHBoxLayout()
            layout.setSpacing(10)

            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            icon_label.setFixedSize(60, 60)
            icon_label.setScaledContents(True)


            info = (
                f"🕒 {dt_txt}\n"
                f"{desc}, {temp}{unit}\n"
                f"💨 Wind: {wind_speed} {speed_unit}\n"
                f"💧 Humidity: {humidity}%\n"
                f"🧭 Pressure: {pressure} hPa"
            )

            text_label = QLabel(info)
            text_label.setFont(QFont("Segoe UI", 11))
            text_label.setWordWrap(True)

            layout.addWidget(icon_label)
            layout.addWidget(text_label)
            forecast_item.setLayout(layout)

            self.forecast_layout.addWidget(forecast_item)

    def voice_search(self):
        city = listen_for_city()
        if city in ["Could not understand", "API unavailable"]:
            QMessageBox.warning(self, "Voice Error", city)
            return

        self.city_input.setText(city)
        self.get_weather()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
.