-- Q3 on the star schema, PostgreSQL dialect.
SELECT
    a.code AS agency,
    c.name AS channel,
    count(*) AS requests,
    count(*) FILTER (WHERE f.closed_within_30d) AS closed_within_30d,
    (count(*) FILTER (WHERE f.closed_within_30d))::double precision / count(*) AS closure_rate
FROM star_pg.fact_service_request f
JOIN star_pg.dim_agency a ON a.agency_key = f.agency_key
JOIN star_pg.dim_channel c ON c.channel_key = f.channel_key
GROUP BY a.code, c.name
ORDER BY a.code COLLATE "C", c.name COLLATE "C";
