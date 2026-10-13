-- Q1: How many requests of each complaint type were created per month in each borough?
SELECT
    l.borough,
    printf('%d-%02d', d.year, d.month) AS month,
    c.complaint_type,
    count(*) AS requests
FROM fact_service_request f
JOIN dim_location l ON l.location_key = f.location_key
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_complaint c ON c.complaint_key = f.complaint_key
GROUP BY l.borough, d.year, d.month, c.complaint_type
ORDER BY l.borough, month, c.complaint_type;
