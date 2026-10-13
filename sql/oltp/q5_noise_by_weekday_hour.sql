-- Q5: In Brooklyn, when do noise complaints concentrate, by day of week and hour?
-- day_of_week follows ISO numbering: 1 = Monday ... 7 = Sunday.
SELECT
    extract(isodow FROM r.created_at)::int AS day_of_week,
    extract(hour FROM r.created_at)::int AS hour,
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
