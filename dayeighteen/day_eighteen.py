"""
Python Learning Journey - Day Eighteen
Date: October 9 2025
Author: Cosmas Onyekwelu
Topic: Working with APIs and Web Data
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_weather(city="Lagos"):
    """
    Fetch current weather data for a given city using OpenWeatherMap API.

    Args:
        city (str): The name of the city to fetch weather for. Defaults to 'Lagos'.

    Returns:
        dict | None: Weather data if successful, otherwise None.
    """
    API_KEY = os.getenv("OPEN_WEATHER_API_KEY")

    if not API_KEY:
        print(
            "Error: Missing API key. Please add 'OPEN_WEATHER_API_KEY' to your .env file.")
        return None

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  # Use Celsius
    }

    try:
        print(f"\nFetching weather data for {city}...")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract weather details
        city_name = data.get("name", city)
        country = data["sys"].get("country", "")
        description = data["weather"][0]["description"].capitalize()
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        # Display formatted weather info
        print("\n" + "=" * 50)
        print(f"WEATHER REPORT — {city_name}, {country}")
        print("=" * 50)
        print(f"Conditions:    {description}")
        print(f"Temperature:   {temperature}°C")
        print(f"Feels Like:    {feels_like}°C")
        print(f"Humidity:      {humidity}%")
        print(f"Wind Speed:    {wind_speed} m/s")
        print("=" * 50)

        # Log to file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("weather_log.txt", "a", encoding="utf-8") as f:
            f.write(
                f"[{timestamp}] {city_name}, {country}: {description}, "
                f"Temp={temperature}°C, FeelsLike={feels_like}°C, "
                f"Humidity={humidity}%, Wind={wind_speed} m/s\n"
            )
        print("Weather data saved to 'weather_log.txt'.")

        return data

    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Invalid API key. Please verify your OpenWeatherMap key.")
        elif response.status_code == 404:
            print("City not found. Please check the spelling.")
        else:
            print(f" HTTP Error: {e}")
    except requests.exceptions.Timeout:
        print("The request timed out. Please try again later.")
    except requests.exceptions.ConnectionError:
        print("Connection error. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        print(f" Request error: {e}")
    except KeyError as e:
        print(f" Missing key in response: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None


def main():
    """Main entry point for the weather app."""
    print("=======================================")
    print("   WEATHER APP — OpenWeatherMap API")
    print("=======================================")
    city = input(
        "Enter city name (press Enter for Lagos): ").strip() or "Lagos"
    get_weather(city)


if __name__ == "__main__":
    main()
