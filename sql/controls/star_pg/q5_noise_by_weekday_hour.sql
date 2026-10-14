-- Q5 on the star schema, PostgreSQL dialect.
-- day_of_week follows ISO numbering: 1 = Monday ... 7 = Sunday.
SELECT
    d.day_of_week::int AS day_of_week,
    f.created_hour::int AS hour,
    count(*) AS requests
FROM star_pg.fact_service_request f
JOIN star_pg.dim_location l ON l.location_key = f.location_key
JOIN star_pg.dim_complaint c ON c.complaint_key = f.complaint_key
JOIN star_pg.dim_date d ON d.date_key = f.date_key
WHERE l.borough = 'BROOKLYN'
  AND c.complaint_type LIKE 'Noise%'
GROUP BY d.day_of_week, f.created_hour
ORDER BY day_of_week, hour;
