-- Populate the star schema from `src_*`, temporary copies of the OLTP tables. Dimensions are
-- flattened and the measures of the fact table are computed once, here.

INSERT INTO dim_agency
SELECT agency_id, code, name FROM src_agency;

INSERT INTO dim_complaint
SELECT d.descriptor_id, t.name, d.name
FROM src_complaint_descriptor d
JOIN src_complaint_type t USING (complaint_type_id);

INSERT INTO dim_location
SELECT l.location_id, b.name, l.zip_code, l.community_board
FROM src_location l
JOIN src_borough b USING (borough_id);

INSERT INTO dim_channel
SELECT channel_id, name FROM src_channel;

INSERT INTO dim_status
SELECT status_id, name FROM src_status;

-- One row per calendar day between the first and the last request loaded.
INSERT INTO dim_date
SELECT
    CAST(strftime(d, '%Y%m%d') AS INTEGER),
    d,
    year(d),
    quarter(d),
    month(d),
    monthname(d),
    day(d),
    isodow(d),
    isodow(d) IN (6, 7)
FROM (
    SELECT CAST(unnest(generate_series(
        CAST(min(created_at) AS DATE), CAST(max(created_at) AS DATE), INTERVAL 1 DAY
    )) AS DATE) AS d
    FROM src_service_request
) AS days;

-- A resolution is valid when the request is closed at or after its creation.
INSERT INTO fact_service_request
SELECT
    request_id,
    CAST(strftime(created_at, '%Y%m%d') AS INTEGER),
    agency_id,
    descriptor_id,
    location_id,
    channel_id,
    status_id,
    created_at,
    hour(created_at),
    closed_at,
    closed_at IS NOT NULL,
    CASE WHEN closed_at >= created_at
         THEN (epoch(closed_at) - epoch(created_at)) / 3600.0 END,
    closed_at IS NOT NULL AND closed_at >= created_at,
    closed_at IS NOT NULL AND closed_at >= created_at
        AND epoch(closed_at) - epoch(created_at) <= 30 * 86400
FROM src_service_request
ORDER BY created_at, request_id;
