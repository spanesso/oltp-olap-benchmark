-- Q5: In Brooklyn, when do noise complaints concentrate, by day of week and hour?
-- day_of_week follows ISO numbering: 1 = Monday ... 7 = Sunday.
SELECT
    CAST(d.day_of_week AS INTEGER) AS day_of_week,
    CAST(f.created_hour AS INTEGER) AS hour,
    count(*) AS requests
FROM fact_service_request f
JOIN dim_location l ON l.location_key = f.location_key
JOIN dim_complaint c ON c.complaint_key = f.complaint_key
JOIN dim_date d ON d.date_key = f.date_key
WHERE l.borough = 'BROOKLYN'
  AND c.complaint_type LIKE 'Noise%'
GROUP BY d.day_of_week, f.created_hour
ORDER BY day_of_week, hour;
