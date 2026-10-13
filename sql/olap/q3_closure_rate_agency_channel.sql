-- Q3: What share of requests does each agency close within 30 days, by channel?
SELECT
    a.code AS agency,
    c.name AS channel,
    count(*) AS requests,
    count(*) FILTER (WHERE f.closed_within_30d) AS closed_within_30d,
    CAST(count(*) FILTER (WHERE f.closed_within_30d) AS DOUBLE) / count(*) AS closure_rate
FROM fact_service_request f
JOIN dim_agency a ON a.agency_key = f.agency_key
JOIN dim_channel c ON c.channel_key = f.channel_key
GROUP BY a.code, c.name
ORDER BY a.code, c.name;
