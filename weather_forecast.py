import sys
from io import BytesIO
from PIL import Image
import requests
import matplotlib.pyplot as plt
from datetime import datetime


def get_daily_forecast(api_key, location, days):
    base_url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": location,
        "days": days,
        "aqi": "yes"
    }
    response = None
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()  # return the response json if no exception
    except requests.exceptions.RequestException:
        if response is not None and hasattr(response, 'json'):
            return response.json()  # return the error json if response exists
        else:
            return None


def analyze_and_plot(api_key, location, days, size):
    # Get the forecast data
    forecast_data = get_daily_forecast(api_key, location, days)

    # If an error occurred and forecast_data is None, don't plot anything
    if forecast_data is None:
        return None, None, None
    elif 'error' in forecast_data:
        return None, forecast_data, None

    # Extract the dates, max temperatures, min temperatures, avg temperatures, and precipitation
    dates = [datetime.strptime(day['date'], "%Y-%m-%d").strftime("%d-%m-%Y") for day in
             forecast_data['forecast']['forecastday']]
    max_temps = [day['day']['maxtemp_c'] for day in forecast_data['forecast']['forecastday']]
    min_temps = [day['day']['mintemp_c'] for day in forecast_data['forecast']['forecastday']]
    avg_temps = [day['day']['avgtemp_c'] for day in forecast_data['forecast']['forecastday']]
    precip = [day['day']['totalprecip_mm'] for day in
              forecast_data['forecast']['forecastday']]

    # Create the plot
    fig, ax1 = plt.subplots(figsize=size)

    ax1.plot(dates, max_temps, marker='o', label='Max Temp', color='tab:red')
    ax1.plot(dates, min_temps, marker='o', label='Min Temp', color='tab:blue')
    ax1.plot(dates, avg_temps, marker='o', label='Avg Temp', color='tab:orange')
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Temperature (°C)", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Rotate x-axis labels
    plt.xticks(rotation=45)

    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.bar(dates, precip, alpha=0.3, color='tab:gray', label='Precipitation')
    ax2.set_ylabel("Precipitation (mm)", color='tab:gray')
    ax2.tick_params(axis='y', labelcolor='tab:gray')
    ax2.legend(loc='upper right')

    # Get the current time and Python version
    current_time = datetime.now()
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    python_version = sys.version

    # Display the current time and Python version in the title
    plt.title(
        f"Temperature and Precipitation Forecast for {location.title()} - Next {days} Days\nGenerated at: {current_time}\nPython Version: {python_version}",
        color='tab:brown', fontsize=8
    )
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image = Image.open(buffer)

    return image, forecast_data, buffer


if __name__ == "__main__":
    api_key = "d6e555e890f043ba8f5105021231912"
    location = "Chirkund"
    days = 14
    _, f, _ = analyze_and_plot(api_key, location, days, (7, 4))
