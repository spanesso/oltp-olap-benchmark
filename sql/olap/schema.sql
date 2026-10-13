-- OLAP model: star schema in DuckDB. Dimensions are denormalized and the fact table carries
-- precomputed measures. Surrogate keys are copied from the OLTP identifiers so both models
-- can be compared row by row. No indexes: columnar scans are the idiomatic access path.

CREATE OR REPLACE TABLE dim_date (
    date_key    integer NOT NULL,   -- yyyymmdd
    date        date NOT NULL,
    year        smallint NOT NULL,
    quarter     tinyint NOT NULL,
    month       tinyint NOT NULL,
    month_name  varchar NOT NULL,
    day         tinyint NOT NULL,
    day_of_week tinyint NOT NULL,   -- ISO: 1 = Monday ... 7 = Sunday
    is_weekend  boolean NOT NULL
);

CREATE OR REPLACE TABLE dim_agency (
    agency_key integer NOT NULL,
    code       varchar NOT NULL,
    name       varchar NOT NULL
);

CREATE OR REPLACE TABLE dim_complaint (
    complaint_key  integer NOT NULL,   -- oltp.complaint_descriptor.descriptor_id
    complaint_type varchar NOT NULL,
    descriptor     varchar NOT NULL
);

CREATE OR REPLACE TABLE dim_location (
    location_key    integer NOT NULL,
    borough         varchar NOT NULL,
    zip_code        varchar NOT NULL,
    community_board varchar NOT NULL
);

CREATE OR REPLACE TABLE dim_channel (
    channel_key integer NOT NULL,
    name        varchar NOT NULL
);

CREATE OR REPLACE TABLE dim_status (
    status_key integer NOT NULL,
    name       varchar NOT NULL
);

CREATE OR REPLACE TABLE fact_service_request (
    request_id           bigint NOT NULL,
    date_key             integer NOT NULL,
    agency_key           integer NOT NULL,
    complaint_key        integer NOT NULL,
    location_key         integer NOT NULL,
    channel_key          integer NOT NULL,
    status_key           integer NOT NULL,
    created_at           timestamp NOT NULL,
    created_hour         tinyint NOT NULL,
    closed_at            timestamp,
    is_closed            boolean NOT NULL,
    -- NULL when the request is open or its closing date precedes its creation date.
    resolution_hours     double,
    has_valid_resolution boolean NOT NULL,
    closed_within_30d    boolean NOT NULL
);
