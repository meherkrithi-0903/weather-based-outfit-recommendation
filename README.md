# MyOutfit

A Streamlit web app that recommends outfits based on real-time weather conditions and your own digital wardrobe.

## Features

- Live weather data via the OpenWeatherMap API
- Considers temperature, humidity, and rain
- Region-aware advice (Indian vs Global comfort standards)
- Digital wardrobe — save your clothes by category, weather, and color
- Picks a matching outfit from your saved wardrobe for the current weather
- Clean, interactive UI built with Streamlit

## Tech Stack

- Python
- Streamlit
- OpenWeatherMap API

## How to Run Locally

1. Clone the repo and install dependencies:
```bash
   pip install -r requirements.txt
```

2. Get a free API key from [OpenWeatherMap](https://home.openweathermap.org/api_keys) and set it as an environment variable:
```bash
   export OPENWEATHER_API_KEY=your_key_here
```

3. Run the app:
```bash
   python3 -m streamlit run app.py
```

4. Open `http://localhost:8501` in your browser if it doesn't launch automatically.

