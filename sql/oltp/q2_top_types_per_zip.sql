-- Q2: For each ZIP code, which are the 10 most frequent complaint types and how long do
-- they take to resolve on average?
WITH per_zip AS (
    SELECT
        l.zip_code,
        ct.name AS complaint_type,
        count(*) AS requests,
        avg(extract(epoch FROM r.closed_at - r.created_at)::double precision / 3600.0)
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
        row_number() OVER (
            PARTITION BY zip_code ORDER BY requests DESC, complaint_type COLLATE "C"
        ) AS rank
    FROM per_zip
)
SELECT zip_code, rank, complaint_type, requests, avg_resolution_hours
FROM ranked
WHERE rank <= 10
ORDER BY zip_code COLLATE "C", rank;
