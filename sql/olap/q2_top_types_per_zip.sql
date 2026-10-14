-- Q2: For each ZIP code, which are the 10 most frequent complaint types and how long do
-- they take to resolve on average?
WITH per_zip AS (
    SELECT
        l.zip_code,
        c.complaint_type,
        count(*) AS requests,
        avg(f.resolution_hours) AS avg_resolution_hours
    FROM fact_service_request f
    JOIN dim_location l ON l.location_key = f.location_key
    JOIN dim_complaint c ON c.complaint_key = f.complaint_key
    GROUP BY l.zip_code, c.complaint_type
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
