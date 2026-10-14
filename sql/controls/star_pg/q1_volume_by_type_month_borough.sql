-- Q1 on the star schema, PostgreSQL dialect.
SELECT
    l.borough,
    d.year::text || '-' || lpad(d.month::text, 2, '0') AS month,
    c.complaint_type,
    count(*) AS requests
FROM star_pg.fact_service_request f
JOIN star_pg.dim_location l ON l.location_key = f.location_key
JOIN star_pg.dim_date d ON d.date_key = f.date_key
JOIN star_pg.dim_complaint c ON c.complaint_key = f.complaint_key
GROUP BY l.borough, d.year, d.month, c.complaint_type
ORDER BY l.borough COLLATE "C", month, c.complaint_type COLLATE "C";
