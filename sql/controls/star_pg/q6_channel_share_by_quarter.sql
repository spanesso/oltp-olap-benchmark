-- Q6 on the star schema, PostgreSQL dialect.
SELECT
    d.year::int AS year,
    d.quarter::int AS quarter,
    c.name AS channel,
    count(*) AS requests,
    count(*)::double precision
        / (sum(count(*)) OVER (PARTITION BY d.year, d.quarter))::double precision AS share
FROM star_pg.fact_service_request f
JOIN star_pg.dim_date d ON d.date_key = f.date_key
JOIN star_pg.dim_channel c ON c.channel_key = f.channel_key
GROUP BY d.year, d.quarter, c.name
ORDER BY year, quarter, c.name COLLATE "C";
