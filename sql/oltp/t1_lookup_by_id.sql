-- T1: read one request by its identifier, with every descriptive attribute.
-- @request_id@ is replaced by the runner with an identifier taken from a fixed list.
SELECT
    r.request_id,
    r.created_at,
    r.closed_at,
    a.code AS agency,
    a.name AS agency_name,
    ct.name AS complaint_type,
    d.name AS descriptor,
    b.name AS borough,
    l.zip_code,
    l.community_board,
    c.name AS channel,
    s.name AS status
FROM oltp.service_request r
JOIN oltp.agency a ON a.agency_id = r.agency_id
JOIN oltp.complaint_descriptor d ON d.descriptor_id = r.descriptor_id
JOIN oltp.complaint_type ct ON ct.complaint_type_id = d.complaint_type_id
JOIN oltp.location l ON l.location_id = r.location_id
JOIN oltp.borough b ON b.borough_id = l.borough_id
JOIN oltp.channel c ON c.channel_id = r.channel_id
JOIN oltp.status s ON s.status_id = r.status_id
WHERE r.request_id = @request_id@;
