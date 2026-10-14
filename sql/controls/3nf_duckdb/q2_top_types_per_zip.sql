-- Q2 on the normalized schema, DuckDB dialect.
WITH per_zip AS (
    SELECT
        l.zip_code,
        ct.name AS complaint_type,
        count(*) AS requests,
        avg(epoch(r.closed_at - r.created_at)::DOUBLE / 3600.0)
            FILTER (WHERE r.closed_at >= r.created_at) AS avg_resolution_hours
    FROM oltp.service_request r
    JOIN oltp.location l ON l.location_id = r.location_id
    JOIN oltp.complaint_descriptor d ON d.descriptor_id = r.descriptor_id
    JOIN oltp.complaint_type ct ON ct.complaint_type_id = d.complaint_type_id
    GROUP BY l.zip_code, ct.name
),
ranked AS (
    SELECT
        *,
        row_number() OVER (PARTITION BY zip_code ORDER BY requests DESC, complaint_type) AS rank
    FROM per_zip
)
SELECT zip_code, rank, complaint_type, requests, avg_resolution_hours
FROM ranked
WHERE rank <= 10
ORDER BY zip_code, rank;
