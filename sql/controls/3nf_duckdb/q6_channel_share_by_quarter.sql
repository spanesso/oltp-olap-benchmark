-- Q6 on the normalized schema, DuckDB dialect.
SELECT
    CAST(extract(year FROM r.created_at) AS INTEGER) AS year,
    CAST(extract(quarter FROM r.created_at) AS INTEGER) AS quarter,
    c.name AS channel,
    count(*) AS requests,
    CAST(count(*) AS DOUBLE) / CAST(sum(count(*)) OVER (
        PARTITION BY extract(year FROM r.created_at), extract(quarter FROM r.created_at)
    ) AS DOUBLE) AS share
FROM oltp.service_request r
JOIN oltp.channel c ON c.channel_id = r.channel_id
GROUP BY extract(year FROM r.created_at), extract(quarter FROM r.created_at), c.name
ORDER BY year, quarter, c.name;
