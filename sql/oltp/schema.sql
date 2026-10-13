-- OLTP model: third normal form. Every descriptive value is stored once and referenced by
-- key; no derived column is stored. The schema is rebuilt from staging on every build.
-- Secondary indexes live in indexes.sql and are created after the bulk load.

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
