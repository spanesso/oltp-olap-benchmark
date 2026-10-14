-- Populate the star schema in PostgreSQL from the OLTP tables. The derived measures are
-- computed once, here, exactly as sql/olap/load.sql does for DuckDB.

INSERT INTO star_pg.dim_agency
SELECT agency_id, code, name FROM oltp.agency;

INSERT INTO star_pg.dim_complaint
SELECT d.descriptor_id, t.name, d.name
FROM oltp.complaint_descriptor d
JOIN oltp.complaint_type t USING (complaint_type_id);

INSERT INTO star_pg.dim_location
SELECT l.location_id, b.name, l.zip_code, l.community_board
FROM oltp.location l
JOIN oltp.borough b USING (borough_id);

INSERT INTO star_pg.dim_channel
SELECT channel_id, name FROM oltp.channel;

INSERT INTO star_pg.dim_status
SELECT status_id, name FROM oltp.status;

-- One row per calendar day between the first and the last request loaded.
INSERT INTO star_pg.dim_date
SELECT
    to_char(d, 'YYYYMMDD')::integer,
    d::date,
    extract(year FROM d)::smallint,
    extract(quarter FROM d)::smallint,
    extract(month FROM d)::smallint,
    to_char(d, 'FMMonth'),
    extract(day FROM d)::smallint,
    extract(isodow FROM d)::smallint,
    extract(isodow FROM d) IN (6, 7)
FROM generate_series(
    (SELECT min(created_at)::date FROM oltp.service_request),
    (SELECT max(created_at)::date FROM oltp.service_request),
    interval '1 day'
) AS days(d);

-- A resolution is valid when the request is closed at or after its creation.
INSERT INTO star_pg.fact_service_request
SELECT
    request_id,
    to_char(created_at, 'YYYYMMDD')::integer,
    agency_id,
    descriptor_id,
    location_id,
    channel_id,
    status_id,
    created_at,
    extract(hour FROM created_at)::smallint,
    closed_at,
    closed_at IS NOT NULL,
    CASE WHEN closed_at >= created_at
         THEN extract(epoch FROM closed_at - created_at)::double precision / 3600.0 END,
    closed_at IS NOT NULL AND closed_at >= created_at,
    closed_at IS NOT NULL AND closed_at >= created_at
        AND extract(epoch FROM closed_at - created_at) <= 30 * 86400
FROM oltp.service_request
ORDER BY created_at, request_id;
