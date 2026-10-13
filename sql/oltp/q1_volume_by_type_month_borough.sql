-- Q1: How many requests of each complaint type were created per month in each borough?
SELECT
    b.name AS borough,
    to_char(date_trunc('month', r.created_at), 'YYYY-MM') AS month,
    ct.name AS complaint_type,
    count(*) AS requests
FROM oltp.service_request r
JOIN oltp.location l ON l.location_id = r.location_id
JOIN oltp.borough b ON b.borough_id = l.borough_id
JOIN oltp.complaint_descriptor d ON d.descriptor_id = r.descriptor_id
JOIN oltp.complaint_type ct ON ct.complaint_type_id = d.complaint_type_id
GROUP BY b.name, date_trunc('month', r.created_at), ct.name
ORDER BY b.name COLLATE "C", month, ct.name COLLATE "C";
