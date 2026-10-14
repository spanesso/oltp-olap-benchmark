-- Control experiment: the star schema of the OLAP model, built inside PostgreSQL.
-- Same tables and columns as sql/olap/schema.sql, so comparing it with the normalized
-- model on the same engine isolates the effect of the schema from the effect of the engine.
-- PostgreSQL has no tinyint; smallint is the closest type. Primary keys match the normalized
-- model, which has one on every table.

DROP SCHEMA IF EXISTS star_pg CASCADE;
CREATE SCHEMA star_pg;

CREATE TABLE star_pg.dim_date (
    date_key    integer PRIMARY KEY,   -- yyyymmdd
    date        date NOT NULL,
    year        smallint NOT NULL,
    quarter     smallint NOT NULL,
    month       smallint NOT NULL,
    month_name  varchar NOT NULL,
    day         smallint NOT NULL,
    day_of_week smallint NOT NULL,  -- ISO: 1 = Monday ... 7 = Sunday
    is_weekend  boolean NOT NULL
);

CREATE TABLE star_pg.dim_agency (
    agency_key integer PRIMARY KEY,
    code       varchar NOT NULL,
    name       varchar NOT NULL
);

CREATE TABLE star_pg.dim_complaint (
    complaint_key  integer PRIMARY KEY,
    complaint_type varchar NOT NULL,
    descriptor     varchar NOT NULL
);

CREATE TABLE star_pg.dim_location (
    location_key    integer PRIMARY KEY,
    borough         varchar NOT NULL,
    zip_code        varchar NOT NULL,
    community_board varchar NOT NULL
);

CREATE TABLE star_pg.dim_channel (
    channel_key integer PRIMARY KEY,
    name        varchar NOT NULL
);

CREATE TABLE star_pg.dim_status (
    status_key integer PRIMARY KEY,
    name       varchar NOT NULL
);

CREATE TABLE star_pg.fact_service_request (
    request_id           bigint PRIMARY KEY,
    date_key             integer NOT NULL,
    agency_key           integer NOT NULL,
    complaint_key        integer NOT NULL,
    location_key         integer NOT NULL,
    channel_key          integer NOT NULL,
    status_key           integer NOT NULL,
    created_at           timestamp NOT NULL,
    created_hour         smallint NOT NULL,
    closed_at            timestamp,
    is_closed            boolean NOT NULL,
    resolution_hours     double precision,
    has_valid_resolution boolean NOT NULL,
    closed_within_30d    boolean NOT NULL
);
