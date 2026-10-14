-- Q5 on the normalized schema, DuckDB dialect.
-- day_of_week follows ISO numbering: 1 = Monday ... 7 = Sunday.
SELECT
    CAST(extract(isodow FROM r.created_at) AS INTEGER) AS day_of_week,
    CAST(extract(hour FROM r.created_at) AS INTEGER) AS hour,
    count(*) AS requests
FROM oltp.service_request r
JOIN oltp.location l ON l.location_id = r.location_id
JOIN oltp.borough b ON b.borough_id = l.borough_id
JOIN oltp.complaint_descriptor d ON d.descriptor_id = r.descriptor_id
JOIN oltp.complaint_type ct ON ct.complaint_type_id = d.complaint_type_id
WHERE b.name = 'BROOKLYN'
  AND ct.name LIKE 'Noise%'
GROUP BY extract(isodow FROM r.created_at), extract(hour FROM r.created_at)
ORDER BY day_of_week, hour;
