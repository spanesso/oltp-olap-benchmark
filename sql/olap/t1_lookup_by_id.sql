-- T1: read one request by its identifier, with every descriptive attribute.
-- @request_id@ is replaced by the runner with an identifier taken from a fixed list.
SELECT
    f.request_id,
    f.created_at,
    f.closed_at,
    a.code AS agency,
    a.name AS agency_name,
    c.complaint_type,
    c.descriptor,
    l.borough,
    l.zip_code,
    l.community_board,
    ch.name AS channel,
    s.name AS status
FROM fact_service_request f
JOIN dim_agency a ON a.agency_key = f.agency_key
JOIN dim_complaint c ON c.complaint_key = f.complaint_key
JOIN dim_location l ON l.location_key = f.location_key
JOIN dim_channel ch ON ch.channel_key = f.channel_key
JOIN dim_status s ON s.status_key = f.status_key
WHERE f.request_id = @request_id@;
