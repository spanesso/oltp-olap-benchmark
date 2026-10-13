-- Q6: How is each quarter's volume split across channels?
SELECT
    CAST(d.year AS INTEGER) AS year,
    CAST(d.quarter AS INTEGER) AS quarter,
    c.name AS channel,
    count(*) AS requests,
    CAST(count(*) AS DOUBLE)
        / CAST(sum(count(*)) OVER (PARTITION BY d.year, d.quarter) AS DOUBLE) AS share
FROM fact_service_request f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_channel c ON c.channel_key = f.channel_key
GROUP BY d.year, d.quarter, c.name
ORDER BY year, quarter, c.name;
