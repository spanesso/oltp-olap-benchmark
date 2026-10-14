-- T2: register one new request. The runner executes it inside a transaction that it rolls
-- back, so the data set does not change. @name@ tokens are replaced by the runner: a new
-- identifier and identifiers of existing dimension members.
INSERT INTO oltp.service_request
    (request_id, created_at, closed_at, agency_id, descriptor_id, location_id, channel_id,
     status_id)
VALUES
    (@request_id@, TIMESTAMP '2026-01-01 12:00:00', NULL, @agency@, @descriptor@, @location@,
     @channel@, @status@);
