import requests
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timezone

CITIES = {
    "Manila": (14.5995, 120.9842),
    "Cebu": (10.3157, 123.8854),
    "Davao": (7.1907, 125.4553),
}

PROJECT_ID = "weather-508506"
DATASET_ID = "weather_raw"
TABLE_ID = "hourly_weather"
CREDENTIALS_PATH = "weather-508506-d731b34cd36a.json"

def fetch_weather(city, lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "Asia/Manila",
        "forecast_days": 1,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Reshape into a flat table: one row per city per hour
    df = pd.DataFrame(data["hourly"])
    df["city"] = city
    df["fetched_at"] = datetime.now(timezone.utc).isoformat()
    return df

def load_to_bigquery(df):
    client = bigquery.Client.from_service_account_json(CREDENTIALS_PATH, project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job = client.load_table_from_dataframe(df, table_ref)
    job.result()  # waits for the load to finish
    print(f"Loaded {len(df)} rows into {table_ref}")

if __name__ == "__main__":
    all_data = []
    for city, (lat, lon) in CITIES.items():
        df = fetch_weather(city, lat, lon)
        all_data.append(df)
        print(f"{city}: {len(df)} hourly records fetched")

    combined = pd.concat(all_data, ignore_index=True)
    load_to_bigquery(combined)