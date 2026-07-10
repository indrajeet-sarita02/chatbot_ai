from tools.weather_tool import get_current_weather, get_weather_forecast

def handle_weather_query(entities: dict, intent: str = "weather_current") -> str:
    city = entities.get("city", "Mumbai")
    is_forecast = intent == "weather_forecast"

    if is_forecast:
        data = get_weather_forecast(city)
        if "error" in data:
            return f"Could not fetch forecast for {city}: {data['error']}"
        lines = [f"🌤️ Weather Forecast for {city}:\n"]
        for day in data.get("forecast", [])[:3]:
            lines.append(
                f"• {day['date']}: {day['condition']}, "
                f"{day['temp_min']}°C - {day['temp_max']}°C, "
                f"Rain: {day['rain_chance']}%"
            )
        return "\n".join(lines)

    data = get_current_weather(city)
    if "error" in data:
        return f"Could not fetch weather for {city}: {data['error']}"
    return (
        f"🌤️ Current Weather in {city}\n"
        f"Temperature: {data['temp']}°C (Feels like {data['feels_like']}°C)\n"
        f"Condition: {data['condition']}\n"
        f"Humidity: {data['humidity']}%\n"
        f"Wind Speed: {data['wind_speed']} km/h\n"
        f"Rain Chance: {data.get('rain_chance', 'N/A')}%"
    )
