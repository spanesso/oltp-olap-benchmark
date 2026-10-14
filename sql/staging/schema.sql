-- Staging area: API pages land here as received. It only ever grows, which is what makes
-- the load idempotent (primary key on unique_key) and resumable (ingest_checkpoint).

CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.service_request_raw (
    -- Collation "C" gives the same byte order the source API uses for its text keys.
    unique_key             text COLLATE "C" PRIMARY KEY,
    created_date           timestamp NOT NULL,
    closed_date            timestamp,
    agency                 text,
    agency_name            text,
    complaint_type         text,
    descriptor             text,
    borough                text,
    incident_zip           text,
    community_board        text,
    open_data_channel_type text,
    status                 text
);

-- The models are built from the first N rows in this order.
CREATE INDEX IF NOT EXISTS service_request_raw_order_idx
    ON staging.service_request_raw (created_date, unique_key);

CREATE TABLE IF NOT EXISTS staging.ingest_checkpoint (
    cut_start         timestamp NOT NULL,
    cut_end           timestamp NOT NULL,
    last_created_date timestamp,
    last_unique_key   text COLLATE "C",
    rows_loaded       bigint NOT NULL DEFAULT 0,
    updated_at        timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (cut_start, cut_end)
);

CREATE TABLE IF NOT EXISTS staging.rejected_row (
    rejected_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    unique_key  text,
    reason      text NOT NULL,
    raw         jsonb NOT NULL,
    rejected_at timestamptz NOT NULL DEFAULT now()
);
