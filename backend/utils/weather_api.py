import requests

def get_weather(location):
    # In a real implementation, you would use a valid API key
    api_key = "YOUR_OPENWEATHER_API_KEY"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + location
    response = requests.get(complete_url)
    weather_data = response.json()

    if weather_data["cod"] != "404":
        main = weather_data["main"]
        temperature = main["temp"]
        humidity = main["humidity"]
        weather_report = weather_data["weather"]
        rainfall = weather_report[0]["description"]

        return {
            "temp": temperature,
            "humidity": humidity,
            "rainfall": rainfall
        }
    else:
        return None