with daily as (
    select
        city,
        date(forecast_time) as forecast_date,
        avg(temperature_2m) as avg_temp,
        max(temperature_2m) as max_temp,
        min(temperature_2m) as min_temp,
        avg(relative_humidity_2m) as avg_humidity,
        sum(precipitation) as total_precipitation
    from {{ ref('stg_weather') }}
    group by city, forecast_date
)

select
    *,
    avg(avg_temp) over (
        partition by city
        order by forecast_date
        rows between 2 preceding and current row
    ) as rolling_3day_avg_temp
from daily
order by city, forecast_date