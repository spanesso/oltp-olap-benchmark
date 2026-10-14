-- Q4 on the normalized schema, DuckDB dialect.
SELECT
    a.code AS agency,
    CAST(extract(year FROM r.created_at) AS INTEGER) AS year,
    CAST(extract(quarter FROM r.created_at) AS INTEGER) AS quarter,
    count(*) AS resolved_requests,
    percentile_cont(0.9) WITHIN GROUP (
        ORDER BY epoch(r.closed_at - r.created_at)::DOUBLE / 3600.0
    ) AS p90_resolution_hours
FROM oltp.service_request r
JOIN oltp.agency a ON a.agency_id = r.agency_id
WHERE r.closed_at >= r.created_at
GROUP BY a.code, extract(year FROM r.created_at), extract(quarter FROM r.created_at)
ORDER BY a.code, year, quarter;
