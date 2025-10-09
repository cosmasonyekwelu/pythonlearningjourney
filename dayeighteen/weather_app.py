import requests
import json
from datetime import datetime


class WeatherApp:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city_name):
        """
        Fetch weather data for a given city
        """
        params = {
            'q': city_name,
            'appid': self.api_key,
            'units': 'metric'
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print("Request timed out. Please try again.")
            return None
        except requests.exceptions.ConnectionError:
            print("Connection error. Check your internet connection.")
            return None
        except requests.exceptions.HTTPError as err:
            if response.status_code == 401:
                print("Invalid API key. Please check your API key.")
            elif response.status_code == 404:
                print("City not found. Please check the city name.")
            else:
                print(f"HTTP error: {err}")
            return None
        except Exception as err:
            print(f"An unexpected error occurred: {err}")
            return None

    def display_weather(self, weather_data):
        """
        Display weather information in a user-friendly format
        """
        if not weather_data:
            return

        try:
            city = weather_data['name']
            country = weather_data['sys']['country']
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            humidity = weather_data['main']['humidity']
            pressure = weather_data['main']['pressure']
            description = weather_data['weather'][0]['description'].title()
            wind_speed = weather_data['wind']['speed']

            print("\n" + "="*50)
            print("WEATHER FORECAST")
            print("="*50)
            print(f"Location:          {city}, {country}")
            print(f"Temperature:       {temp}°C")
            print(f"Feels like:        {feels_like}°C")
            print(f"Humidity:          {humidity}%")
            print(f"Pressure:          {pressure} hPa")
            print(f"Wind Speed:        {wind_speed} m/s")
            print(f"Conditions:        {description}")
            print("="*50)

        except KeyError as err:
            print(f"Error parsing weather data: Missing key {err}")

    def save_to_file(self, weather_data, filename="weather_history.json"):
        """
        Save weather data to a JSON file
        """
        try:
            data_to_save = weather_data.copy()
            data_to_save['retrieved_at'] = datetime.now().isoformat()

            try:
                with open(filename, 'r') as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []

            if not isinstance(existing_data, list):
                existing_data = [existing_data]

            existing_data.append(data_to_save)

            with open(filename, 'w') as f:
                json.dump(existing_data, f, indent=2)

            print(f"Weather data saved to {filename}")

        except Exception as err:
            print(f"Error saving to file: {err}")


def display_weather_history(filename="weather_history.json"):
    """
    Display previously saved weather data
    """
    try:
        with open(filename, 'r') as f:
            history_data = json.load(f)

        if not history_data:
            print("No weather history found.")
            return

        print("\n" + "="*50)
        print("WEATHER HISTORY")
        print("="*50)

        for i, entry in enumerate(history_data[-5:], 1):
            city = entry.get('name', 'Unknown')
            country = entry.get('sys', {}).get('country', 'Unknown')
            temp = entry.get('main', {}).get('temp', 'Unknown')
            timestamp = entry.get('retrieved_at', 'Unknown')

            date_obj = datetime.fromisoformat(timestamp)
            formatted_time = date_obj.strftime("%Y-%m-%d %H:%M:%S")

            print(f"{i}. {city}, {country} - {temp}°C at {formatted_time}")

        print("="*50)

    except FileNotFoundError:
        print("No weather history file found.")
    except Exception as err:
        print(f"Error reading history file: {err}")


def temperature_conversion():
    """
    Utility function for temperature conversion
    """
    print("\nTemperature Conversion")
    print("1. Celsius to Fahrenheit")
    print("2. Fahrenheit to Celsius")

    choice = input("Choose conversion type (1-2): ").strip()

    if choice == '1':
        try:
            celsius = float(input("Enter temperature in Celsius: "))
            fahrenheit = (celsius * 9/5) + 32
            print(f"{celsius}°C = {fahrenheit:.1f}°F")
        except ValueError:
            print("Invalid temperature value.")

    elif choice == '2':
        try:
            fahrenheit = float(input("Enter temperature in Fahrenheit: "))
            celsius = (fahrenheit - 32) * 5/9
            print(f"{fahrenheit}°F = {celsius:.1f}°C")
        except ValueError:
            print("Invalid temperature value.")

    else:
        print("Invalid choice.")


def main():
    API_KEY = "ffd48f44ebf3038d180bee97399ebc81"

    weather_app = WeatherApp(API_KEY)

    print("Welcome to the Weather Application")
    print("Get current weather information for any city worldwide.")

    while True:
        print("\nMain Menu:")
        print("1. Check current weather")
        print("2. View weather history")
        print("3. Temperature conversion")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            city = input("Enter city name: ").strip()

            if not city:
                print("Please enter a valid city name.")
                continue

            print(f"Fetching weather data for {city}...")
            weather_data = weather_app.get_weather(city)

            if weather_data:
                weather_app.display_weather(weather_data)

                save_choice = input(
                    "Save this data to file? (y/n): ").strip().lower()
                if save_choice in ['y', 'yes']:
                    weather_app.save_to_file(weather_data)

        elif choice == '2':
            display_weather_history()

        elif choice == '3':
            temperature_conversion()

        elif choice == '4':
            print("Thank you for using the Weather Application! Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1-4.")


if __name__ == "__main__":
    main()
