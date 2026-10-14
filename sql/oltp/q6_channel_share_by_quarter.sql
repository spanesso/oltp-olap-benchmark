-- Q6: How is each quarter's volume split across channels?
SELECT
    extract(year FROM r.created_at)::int AS year,
    extract(quarter FROM r.created_at)::int AS quarter,
    c.name AS channel,
    count(*) AS requests,
    count(*)::double precision / (
        sum(count(*)) OVER (
            PARTITION BY extract(year FROM r.created_at), extract(quarter FROM r.created_at)
        )
    )::double precision AS share
FROM oltp.service_request r
JOIN oltp.channel c ON c.channel_id = r.channel_id
GROUP BY extract(year FROM r.created_at), extract(quarter FROM r.created_at), c.name
ORDER BY year, quarter, c.name COLLATE "C";
