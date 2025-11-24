# Day 18 - Python Learning Journey

**Date:** October 9, 2025

## Topic: Working with APIs and Web Data

**Focus:** Fetching and processing data from external APIs

---

## Activities

1. Learned how to use the `requests` library for making API calls.
2. Understood how to parse and process JSON responses.
3. Implemented error handling for network requests and timeouts.
4. Practiced REST API integration using OpenWeatherMap.
5. Built a complete **Weather Application** that fetches real-time weather data for any city.
6. Added data persistence to store and review weather history.
7. Installed and configured the python-dotenv library.
8. Created and loaded a .env file to store sensitive environment variables.
9. Used os.getenv() to securely access API keys from environment variables.
10. Practiced secure API integration using requests and environment configuration.
11. Improved code structure for reusability and better security practices.

---

## Files Overview

### **1. day_eighteen.py**

Main entry script that initializes and runs the weather application.

- Handles menu navigation
- Manages user input
- Calls functions from `weather_app.py`

### **2. weather_app.py**

Contains the `WeatherApp` class and supporting utility functions.

- Handles API requests, JSON processing, and error handling
- Saves and loads weather data to/from JSON files
- Includes temperature conversion utility

---

## Setup Instructions

### 1. Navigate to your Day 18 folder

```bash
cd pythonlearningjourney/day_eighteen
```

## Key Learnings

- Integrated third-party APIs using the requests library.
- Parsed JSON responses and handled data programmatically.
- Implemented exception handling for:
- Timeouts
- Invalid city names
- Invalid API keys
- Network issues
- Saved and reloaded data using JSON persistence.
- Created utility functions for temperature conversions and historical data tracking.
- Never hardcode API keys in your code.
- Use .env files and python-dotenv for secure key management.
- Always handle missing environment variables gracefully.
- Keep .env files private and add them to .gitignore

## Reflection

This project demonstrated how to connect Python with real-world web data. Building a Weather App reinforced the importance of:

- Proper API error handling
- JSON serialization and deserialization
- Data persistence and modular programming.

I successfully built a complete, user-friendly Python application that interacts with a live API and saves user data locally.
