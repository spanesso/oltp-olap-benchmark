-- OLTP model: third normal form. Every descriptive value is stored once and referenced by
-- key; no derived column is stored. The schema is rebuilt from staging on every build.

DROP SCHEMA IF EXISTS oltp CASCADE;
CREATE SCHEMA oltp;

CREATE TABLE oltp.agency (
    agency_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code      text NOT NULL,
    name      text NOT NULL,
    UNIQUE (code, name)
);

CREATE TABLE oltp.complaint_type (
    complaint_type_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name              text NOT NULL UNIQUE
);

CREATE TABLE oltp.complaint_descriptor (
    descriptor_id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    complaint_type_id integer NOT NULL REFERENCES oltp.complaint_type (complaint_type_id),
    name              text NOT NULL,
    UNIQUE (complaint_type_id, name)
);

CREATE TABLE oltp.borough (
    borough_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       text NOT NULL UNIQUE
);

CREATE TABLE oltp.location (
    location_id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    borough_id      integer NOT NULL REFERENCES oltp.borough (borough_id),
    zip_code        text NOT NULL,
    community_board text NOT NULL,
    UNIQUE (borough_id, zip_code, community_board)
);

CREATE TABLE oltp.channel (
    channel_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       text NOT NULL UNIQUE
);

CREATE TABLE oltp.status (
    status_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name      text NOT NULL UNIQUE
);

CREATE TABLE oltp.service_request (
    request_id    bigint PRIMARY KEY,
    created_at    timestamp NOT NULL,
    closed_at     timestamp,
    agency_id     integer NOT NULL REFERENCES oltp.agency (agency_id),
    descriptor_id integer NOT NULL REFERENCES oltp.complaint_descriptor (descriptor_id),
    location_id   integer NOT NULL REFERENCES oltp.location (location_id),
    channel_id    integer NOT NULL REFERENCES oltp.channel (channel_id),
    status_id     integer NOT NULL REFERENCES oltp.status (status_id)
);

-- Indexes a transactional workload would have: one per foreign key, plus creation time.
CREATE INDEX service_request_agency_idx     ON oltp.service_request (agency_id);
CREATE INDEX service_request_descriptor_idx ON oltp.service_request (descriptor_id);
CREATE INDEX service_request_location_idx   ON oltp.service_request (location_id);
CREATE INDEX service_request_channel_idx    ON oltp.service_request (channel_id);
CREATE INDEX service_request_status_idx     ON oltp.service_request (status_id);
CREATE INDEX service_request_created_at_idx ON oltp.service_request (created_at);
CREATE INDEX complaint_descriptor_type_idx  ON oltp.complaint_descriptor (complaint_type_id);
CREATE INDEX location_borough_idx           ON oltp.location (borough_id);
