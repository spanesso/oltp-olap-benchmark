-- Q4 on the star schema, PostgreSQL dialect.
SELECT
    a.code AS agency,
    d.year::int AS year,
    d.quarter::int AS quarter,
    count(*) AS resolved_requests,
    percentile_cont(0.9) WITHIN GROUP (ORDER BY f.resolution_hours) AS p90_resolution_hours
FROM star_pg.fact_service_request f
JOIN star_pg.dim_agency a ON a.agency_key = f.agency_key
JOIN star_pg.dim_date d ON d.date_key = f.date_key
WHERE f.has_valid_resolution
GROUP BY a.code, d.year, d.quarter
ORDER BY a.code COLLATE "C", year, quarter;
