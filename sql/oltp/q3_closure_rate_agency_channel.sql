-- Q3: What share of requests does each agency close within 30 days, by channel?
SELECT
    a.code AS agency,
    c.name AS channel,
    count(*) AS requests,
    count(*) FILTER (
        WHERE r.closed_at >= r.created_at AND r.closed_at - r.created_at <= interval '30 days'
    ) AS closed_within_30d,
    count(*) FILTER (
        WHERE r.closed_at >= r.created_at AND r.closed_at - r.created_at <= interval '30 days'
    )::double precision / count(*) AS closure_rate
FROM oltp.service_request r
JOIN oltp.agency a ON a.agency_id = r.agency_id
JOIN oltp.channel c ON c.channel_id = r.channel_id
GROUP BY a.code, c.name
ORDER BY a.code COLLATE "C", c.name COLLATE "C";
