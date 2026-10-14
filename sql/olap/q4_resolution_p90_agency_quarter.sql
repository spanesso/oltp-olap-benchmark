-- Q4: What is the 90th percentile of resolution time per agency and quarter?
SELECT
    a.code AS agency,
    CAST(d.year AS INTEGER) AS year,
    CAST(d.quarter AS INTEGER) AS quarter,
    count(*) AS resolved_requests,
    quantile_cont(f.resolution_hours, 0.9) AS p90_resolution_hours
FROM fact_service_request f
JOIN dim_agency a ON a.agency_key = f.agency_key
JOIN dim_date d ON d.date_key = f.date_key
WHERE f.has_valid_resolution
GROUP BY a.code, d.year, d.quarter
ORDER BY a.code, year, quarter;
