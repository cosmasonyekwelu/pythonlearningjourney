"""
Weather Application — OpenWeatherMap API
----------------------------------------
This Python script provides a complete command-line interface to:
- Fetch current weather information for any city.
- Display and store weather history locally.
- Perform temperature conversions between Celsius and Fahrenheit.

Features:
    • Reads API key from .env file (OPENWEATHER_API_KEY)
    • Handles errors gracefully (invalid city, network issues, etc.)
    • Saves and loads data in JSON format
    • Clean, professional console output

Author: Cosmas Onyekwelu
Date: October 9, 2025
"""

import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()


class WeatherApp:
    """
    A class that interacts with the OpenWeatherMap API to retrieve,
    display, and store weather data.
    """

    def __init__(self, api_key):
        """
        Initialize the WeatherApp with the API key.

        Args:
            api_key (str): The OpenWeatherMap API key.
        """
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city_name):
        """
        Fetch weather data for a given city.

        Args:
            city_name (str): Name of the city to fetch weather data for.

        Returns:
            dict | None: Weather data if successful, otherwise None.
        """
        params = {
            "q": city_name,
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print("Error: Request timed out. Please try again later.")
        except requests.exceptions.ConnectionError:
            print("Error: Network connection issue. Check your internet connection.")
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                print("Error: Invalid API key. Please verify your key in the .env file.")
            elif response.status_code == 404:
                print("Error: City not found. Please check the city name.")
            else:
                print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"Unexpected error: {err}")

        return None

    def display_weather(self, weather_data):
        """
        Display weather information in a readable format.

        Args:
            weather_data (dict): The weather data dictionary.
        """
        if not weather_data:
            return

        try:
            city = weather_data["name"]
            country = weather_data["sys"]["country"]
            temp = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            humidity = weather_data["main"]["humidity"]
            pressure = weather_data["main"]["pressure"]
            description = weather_data["weather"][0]["description"].capitalize(
            )
            wind_speed = weather_data["wind"]["speed"]

            print("\n" + "=" * 50)
            print("CURRENT WEATHER REPORT")
            print("=" * 50)
            print(f"Location:        {city}, {country}")
            print(f"Temperature:     {temp}°C")
            print(f"Feels Like:      {feels_like}°C")
            print(f"Humidity:        {humidity}%")
            print(f"Pressure:        {pressure} hPa")
            print(f"Wind Speed:      {wind_speed} m/s")
            print(f"Conditions:      {description}")
            print("=" * 50)

        except KeyError as err:
            print(f"Error: Missing expected data field ({err}).")

    def save_to_file(self, weather_data, filename="weather_history.json"):
        """
        Save fetched weather data to a JSON file.

        Args:
            weather_data (dict): The weather data dictionary.
            filename (str): The filename to save to.
        """
        try:
            # Include a timestamp for tracking
            data_to_save = weather_data.copy()
            data_to_save["retrieved_at"] = datetime.now().isoformat()

            try:
                with open(filename, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []

            # Ensure list format
            if not isinstance(existing_data, list):
                existing_data = [existing_data]

            existing_data.append(data_to_save)

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2)

            print(f"Weather data saved successfully to {filename}.")

        except Exception as err:
            print(f"Error saving to file: {err}")


def display_weather_history(filename="weather_history.json"):
    """
    Display previously saved weather history.

    Args:
        filename (str): The history file to read from.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            history_data = json.load(f)

        if not history_data:
            print("No weather history available.")
            return

        print("\n" + "=" * 50)
        print("WEATHER HISTORY")
        print("=" * 50)

        for i, entry in enumerate(history_data[-5:], 1):
            city = entry.get("name", "Unknown")
            country = entry.get("sys", {}).get("country", "Unknown")
            temp = entry.get("main", {}).get("temp", "Unknown")
            timestamp = entry.get("retrieved_at", "Unknown")

            try:
                date_obj = datetime.fromisoformat(timestamp)
                formatted_time = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                formatted_time = "Unknown time"

            print(f"{i}. {city}, {country} - {temp}°C (Saved at {formatted_time})")

        print("=" * 50)

    except FileNotFoundError:
        print("No weather history file found.")
    except Exception as err:
        print(f"Error reading history: {err}")


def temperature_conversion():
    """
    Convert temperature between Celsius and Fahrenheit.
    """
    print("\nTemperature Conversion Tool")
    print("1. Celsius to Fahrenheit")
    print("2. Fahrenheit to Celsius")

    choice = input("Select conversion type (1 or 2): ").strip()

    if choice == "1":
        try:
            celsius = float(input("Enter temperature in Celsius: "))
            fahrenheit = (celsius * 9 / 5) + 32
            print(f"{celsius}°C = {fahrenheit:.2f}°F")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    elif choice == "2":
        try:
            fahrenheit = float(input("Enter temperature in Fahrenheit: "))
            celsius = (fahrenheit - 32) * 5 / 9
            print(f"{fahrenheit}°F = {celsius:.2f}°C")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    else:
        print("Invalid selection. Please enter 1 or 2.")


def main():
    """
    Main entry point for the Weather Application.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        print("Error: Missing API key. Please add OPENWEATHER_API_KEY to your .env file.")
        return

    weather_app = WeatherApp(api_key)

    print("==========================================")
    print("        WEATHER APPLICATION (CLI)         ")
    print("==========================================")
    print("Retrieve and log real-time weather data for any city.\n")

    while True:
        print("\nMain Menu")
        print("------------------------------------------")
        print("1. Check current weather")
        print("2. View saved weather history")
        print("3. Temperature conversion")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            city = input("Enter city name: ").strip()
            if not city:
                print("Please enter a valid city name.")
                continue

            print(f"\nFetching weather data for {city}...")
            weather_data = weather_app.get_weather(city)

            if weather_data:
                weather_app.display_weather(weather_data)
                save_choice = input("Save this data? (y/n): ").strip().lower()
                if save_choice in ("y", "yes"):
                    weather_app.save_to_file(weather_data)

        elif choice == "2":
            display_weather_history()

        elif choice == "3":
            temperature_conversion()

        elif choice == "4":
            print("\nThank you for using the Weather Application. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
