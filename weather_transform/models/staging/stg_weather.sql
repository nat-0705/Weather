with raw_weather as (
    select
        city,
        parse_datetime('%Y-%m-%dT%H:%M', time) as forecast_time,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        fetched_at
    from `weather-508506.weather_raw.hourly_weather`
),

deduped as (
    select
        *,
        row_number() over (
            partition by city, forecast_time
            order by fetched_at desc
        ) as row_num
    from raw_weather
)

select
    city,
    forecast_time,
    temperature_2m,
    relative_humidity_2m,
    precipitation,
    fetched_at
from deduped
where row_num = 1