-- Secondary indexes of the OLTP model, created after the bulk load because building them
-- once is much faster than maintaining them row by row.
-- What a transactional workload would have: one per foreign key, plus creation time.
CREATE INDEX service_request_agency_idx     ON oltp.service_request (agency_id);
CREATE INDEX service_request_descriptor_idx ON oltp.service_request (descriptor_id);
CREATE INDEX service_request_location_idx   ON oltp.service_request (location_id);
CREATE INDEX service_request_channel_idx    ON oltp.service_request (channel_id);
CREATE INDEX service_request_status_idx     ON oltp.service_request (status_id);
CREATE INDEX service_request_created_at_idx ON oltp.service_request (created_at);
CREATE INDEX complaint_descriptor_type_idx  ON oltp.complaint_descriptor (complaint_type_id);
CREATE INDEX location_borough_idx           ON oltp.location (borough_id);
