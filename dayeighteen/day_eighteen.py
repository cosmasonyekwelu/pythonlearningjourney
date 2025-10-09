import requests
from datetime import datetime


def get_weather(city="Lagos"):
    """
    Fetches current weather data for a given city using OpenWeatherMap API.
    Requires a valid API key from https://openweathermap.org/api.
    """

    API_KEY = "82b584e5405d5d9aec26457c8753e389"
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  # Use Celsius
    }

    try:
        # Send GET request to API
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()  # Raises error for non-200 responses
        data = response.json()

        # Extract important data
        weather_desc = data["weather"][0]["description"].capitalize()
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        # Display formatted results
        print("\n--- Current Weather Report ---")
        print(f"City: {city}")
        print(f"Weather: {weather_desc}")
        print(f"Temperature: {temperature}°C")
        print(f"Feels Like: {feels_like}°C")
        print(f"Humidity: {humidity}%")
        print(f"Wind Speed: {wind_speed} m/s")

        # Save results to a local log file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("weather_log.txt", "a") as log_file:
            log_file.write(
                f"[{timestamp}] {city} - {weather_desc}, Temp: {temperature}°C, "
                f"Feels Like: {feels_like}°C, Humidity: {humidity}%, Wind: {wind_speed} m/s\n"
            )

        print("\nWeather data saved to 'weather_log.txt'.")

    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)
    except requests.exceptions.Timeout:
        print("The request timed out. Please check your network connection.")
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
    except KeyError:
        print(
            "Unexpected data format from the API. Please verify your API key or city name.")


if __name__ == "__main__":
    print("Weather App - Lagos, Nigeria")
    city_input = input("Enter city name (press Enter for Lagos): ").strip()
    if not city_input:
        city_input = "Lagos"
    get_weather(city_input)
