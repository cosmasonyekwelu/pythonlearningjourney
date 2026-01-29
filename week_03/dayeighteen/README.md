# Day 18: Working with APIs and Web Data

**Date:** October 9, 2025

## Learning Objective
To understand how to interact with external web services using REST APIs, handle HTTP requests, and process JSON responses.

## Concepts Covered
- **HTTP Requests**: Using the `requests` library to perform GET requests.
- **API Keys**: Managing sensitive credentials using environment variables and the `python-dotenv` package.
- **JSON Parsing**: Converting web responses into Python dictionaries.
- **Error Handling in Networking**: Handling timeouts, connection errors, and HTTP status codes (e.g., 401 Unauthorized, 404 Not Found).
- **Data Logging**: Recording API data to a local log file for history tracking.

## Code Explanation
The `day_eighteen.py` script implements a Weather Application:
- **`get_weather(city)`**:
    - Fetches an API key from environment variables.
    - Constructs a URL for the OpenWeatherMap API.
    - Sends a request and validates the status using `response.raise_for_status()`.
    - Parses the temperature, humidity, and wind speed.
    - Appends the result to `weather_log.txt`.
- **Environment Management**: Demonstrates the best practice of using a `.env` file instead of hardcoding API keys.

## How to Run
1. Install requirements: `pip install requests python-dotenv`
2. Create a `.env` file and add: `OPEN_WEATHER_API_KEY=your_key_here`
3. Run the application:
```bash
python week_03/dayeighteen/day_eighteen.py
```

## Reflection
APIs connect Python to the real world. Learning to handle the unpredictability of network requests—like slow connections or invalid inputs—is a critical skill for any modern developer.
