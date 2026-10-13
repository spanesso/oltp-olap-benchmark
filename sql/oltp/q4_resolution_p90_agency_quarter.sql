-- Q4: What is the 90th percentile of resolution time per agency and quarter?
SELECT
    a.code AS agency,
    extract(year FROM r.created_at)::int AS year,
    extract(quarter FROM r.created_at)::int AS quarter,
    count(*) AS resolved_requests,
    percentile_cont(0.9) WITHIN GROUP (
        ORDER BY extract(epoch FROM r.closed_at - r.created_at)::double precision / 3600.0
    ) AS p90_resolution_hours
FROM oltp.service_request r
JOIN oltp.agency a ON a.agency_id = r.agency_id
WHERE r.closed_at >= r.created_at
GROUP BY a.code, extract(year FROM r.created_at), extract(quarter FROM r.created_at)
ORDER BY a.code COLLATE "C", year, quarter;
