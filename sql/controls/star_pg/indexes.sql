-- The same kind of indexes the normalized model has: a primary key on every table (see
-- schema.sql), one index per foreign key of the fact table, plus creation time. Without them
-- the control would unfairly handicap PostgreSQL.
CREATE INDEX fact_agency_idx     ON star_pg.fact_service_request (agency_key);
CREATE INDEX fact_complaint_idx  ON star_pg.fact_service_request (complaint_key);
CREATE INDEX fact_location_idx   ON star_pg.fact_service_request (location_key);
CREATE INDEX fact_channel_idx    ON star_pg.fact_service_request (channel_key);
CREATE INDEX fact_status_idx     ON star_pg.fact_service_request (status_key);
CREATE INDEX fact_date_idx       ON star_pg.fact_service_request (date_key);
CREATE INDEX fact_created_at_idx ON star_pg.fact_service_request (created_at);
