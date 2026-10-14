-- Q3 on the normalized schema, DuckDB dialect.
SELECT
    a.code AS agency,
    c.name AS channel,
    count(*) AS requests,
    count(*) FILTER (
        WHERE r.closed_at >= r.created_at AND r.closed_at - r.created_at <= INTERVAL 30 DAY
    ) AS closed_within_30d,
    CAST(count(*) FILTER (
        WHERE r.closed_at >= r.created_at AND r.closed_at - r.created_at <= INTERVAL 30 DAY
    ) AS DOUBLE) / count(*) AS closure_rate
FROM oltp.service_request r
JOIN oltp.agency a ON a.agency_id = r.agency_id
JOIN oltp.channel c ON c.channel_id = r.channel_id
GROUP BY a.code, c.name
ORDER BY a.code, c.name;
