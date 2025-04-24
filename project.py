
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from weather_logic import fetch_weather, fetch_forecast, get_weather_emoji

class WeatherLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        self.unit = "metric"

        self.city_input = TextInput(hint_text="Enter city", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.city_input)

        self.unit_spinner = Spinner(
            text='Celsius',
            values=('Celsius', 'Fahrenheit'),
            size_hint_y=None, height=40
        )
        self.unit_spinner.bind(text=self.change_unit)
        self.add_widget(self.unit_spinner)

        self.search_button = Button(text="Search", size_hint_y=None, height=40)
        self.search_button.bind(on_press=self.get_weather)
        self.add_widget(self.search_button)

        self.result_label = Label(text='', size_hint_y=None, height=100)
        self.add_widget(self.result_label)

        self.forecast_label = Label(text='', size_hint_y=1)
        self.add_widget(self.forecast_label)

    def change_unit(self, spinner, text):
        self.unit = "metric" if text == "Celsius" else "imperial"

    def get_weather(self, instance):
        city = self.city_input.text
        current = fetch_weather(city, self.unit)
        forecast = fetch_forecast(city, self.unit)

        if current.get("cod") != 200:
            self.result_label.text = "❌ City not found."
            return

        temp = current["main"]["temp"]
        desc = current["weather"][0]["description"].title()
        emoji = get_weather_emoji(current["weather"][0]["id"])
        unit_symbol = "°C" if self.unit == "metric" else "°F"

        self.result_label.text = f"{emoji} {desc}\nTemperature: {temp}{unit_symbol}"

        # Forecast
        forecast_data = forecast.get("list", [])
        forecast_text = "[b]5-Day Forecast:[/b]\n"
        shown_dates = set()
        for entry in forecast_data:
            dt_txt = entry["dt_txt"]
            date, time = dt_txt.split()
            if time == "12:00:00" and date not in shown_dates:
                f_temp = entry["main"]["temp"]
                f_desc = entry["weather"][0]["description"].title()
                f_emoji = get_weather_emoji(entry["weather"][0]["id"])
                forecast_text += f"{date}: {f_emoji} {f_desc}, {f_temp}°\n"
                shown_dates.add(date)

        self.forecast_label.text = forecast_text


class WeatherApp(App):
    def build(self):
        self.title = "Weather App"
        return WeatherLayout()

if __name__ == "__main__":
    WeatherApp().run()
