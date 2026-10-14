-- Populate the OLTP model from `build_source`, a temporary table holding the first N staged
-- rows with missing values already mapped to 'Unknown'. Lookup tables first, then requests.
-- ORDER BY makes the generated identifiers reproducible between builds.

INSERT INTO oltp.agency (code, name)
SELECT DISTINCT agency_code, agency_name FROM build_source ORDER BY 1, 2;

INSERT INTO oltp.complaint_type (name)
SELECT DISTINCT complaint_type FROM build_source ORDER BY 1;

INSERT INTO oltp.complaint_descriptor (complaint_type_id, name)
SELECT DISTINCT ct.complaint_type_id, s.descriptor
FROM build_source s
JOIN oltp.complaint_type ct ON ct.name = s.complaint_type
ORDER BY 1, 2;

INSERT INTO oltp.borough (name)
SELECT DISTINCT borough FROM build_source ORDER BY 1;

INSERT INTO oltp.location (borough_id, zip_code, community_board)
SELECT DISTINCT b.borough_id, s.zip_code, s.community_board
FROM build_source s
JOIN oltp.borough b ON b.name = s.borough
ORDER BY 1, 2, 3;

INSERT INTO oltp.channel (name)
SELECT DISTINCT channel FROM build_source ORDER BY 1;

INSERT INTO oltp.status (name)
SELECT DISTINCT status FROM build_source ORDER BY 1;

INSERT INTO oltp.service_request
    (request_id, created_at, closed_at, agency_id, descriptor_id, location_id, channel_id, status_id)
SELECT
    s.request_id,
    s.created_at,
    s.closed_at,
    a.agency_id,
    d.descriptor_id,
    l.location_id,
    c.channel_id,
    st.status_id
FROM build_source s
JOIN oltp.agency a ON a.code = s.agency_code AND a.name = s.agency_name
JOIN oltp.complaint_type ct ON ct.name = s.complaint_type
JOIN oltp.complaint_descriptor d
    ON d.complaint_type_id = ct.complaint_type_id AND d.name = s.descriptor
JOIN oltp.borough b ON b.name = s.borough
JOIN oltp.location l
    ON l.borough_id = b.borough_id
    AND l.zip_code = s.zip_code
    AND l.community_board = s.community_board
JOIN oltp.channel c ON c.name = s.channel
JOIN oltp.status st ON st.name = s.status;
