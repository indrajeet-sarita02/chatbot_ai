import requests

BASE_URL = "https://wttr.in"

def get_current_weather(city: str) -> dict:
    try:
        resp = requests.get(f"{BASE_URL}/{city}?format=j1", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cc = data["current_condition"][0]
        return {
            "temp": float(cc["temp_C"]),
            "feels_like": float(cc["FeelsLikeC"]),
            "condition": cc["weatherDesc"][0]["value"],
            "humidity": int(cc["humidity"]),
            "wind_speed": float(cc["windspeedKmph"]),
            "city": data["nearest_area"][0]["areaName"][0]["value"],
        }
    except Exception as e:
        return {"error": str(e)}

def get_weather_forecast(city: str) -> dict:
    try:
        resp = requests.get(f"{BASE_URL}/{city}?format=j1", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        forecast = []
        for day in data["weather"]:
            forecast.append({
                "date": day["date"],
                "temp_min": float(day["mintempC"]),
                "temp_max": float(day["maxtempC"]),
                "condition": day["hourly"][0]["weatherDesc"][0]["value"],
                "rain_chance": int(day["hourly"][0].get("chanceofrain", "0")),
                "humidity": int(day["hourly"][0]["humidity"]),
            })
        return {"forecast": forecast, "city": data["nearest_area"][0]["areaName"][0]["value"]}
    except Exception as e:
        return {"error": str(e)}
