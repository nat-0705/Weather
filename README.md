# PH Weather & Climate Data Pipeline

An automated data pipeline that ingests hourly weather data for major Philippine cities, transforms it into clean, analysis-ready tables using a medallion architecture, and visualizes trends in a public dashboard.

Built as a companion project to [MedGreen](#) (an AI plant-identification app), this pipeline demonstrates how environmental data can be collected and modeled to support agriculture and plant-health use cases.

**Live Dashboard:** https://datastudio.google.com/reporting/ab7f4cdb-d35c-45e3-8d9c-d2b6249dbce7

## Architecture

```
Open-Meteo API (source)
        │
        ▼
Python ingestion script ──► scheduled daily via GitHub Actions
        │
        ▼
BigQuery — weather_raw (bronze: raw hourly forecasts)
        │
        ▼
dbt Core transformation
        │
        ├── stg_weather (silver: deduplicated, cleaned)
        │
        ▼
daily_weather_summary (gold: daily aggregates + rolling 3-day avg temp)
        │
        ▼
Looker Studio dashboard
```

## Tools Used

| Layer | Tool |
|---|---|
| Data source | [Open-Meteo API](https://open-meteo.com/) (free, no key required) |
| Ingestion | Python (`requests`, `pandas`) |
| Orchestration | GitHub Actions (daily cron schedule) |
| Warehouse | Google BigQuery (free tier) |
| Transformation | dbt Core |
| Visualization | Looker Studio |

## What This Project Demonstrates

- **Automated daily ingestion** — a Python script pulls hourly weather data (temperature, humidity, precipitation) for Manila, Cebu, and Davao, running unattended via a scheduled GitHub Actions workflow.
- **Medallion architecture** — raw data (bronze) is deduplicated and cleaned into a staging layer (silver) using SQL window functions, then aggregated into business-ready daily summaries (gold).
- **Data quality testing** — dbt tests enforce not-null constraints on key fields before data is considered trustworthy.
- **Secure credential handling** — service account keys are never committed to version control; they're injected at runtime via GitHub Secrets.
- **Window functions in practice** — `ROW_NUMBER()` for deduplication and a rolling 3-day average using `AVG() OVER (...)` for trend smoothing.

## Key SQL Pattern (Deduplication)

```sql
with deduped as (
    select
        *,
        row_number() over (
            partition by city, forecast_time
            order by fetched_at desc
        ) as row_num
    from raw_weather
)
select * from deduped where row_num = 1
```

## Data Source

Weather data provided by [Open-Meteo.com](https://open-meteo.com/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Future Improvements

- Expand to more cities/regions across the Philippines
- Add anomaly detection for extreme weather alerts
- Backfill historical data using Open-Meteo's archive API
- Integrate air quality data to connect back to the MedGreen plant-health use case