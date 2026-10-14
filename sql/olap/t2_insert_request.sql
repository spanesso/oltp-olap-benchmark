-- T2: register one new request. The runner executes it inside a transaction that it rolls
-- back, so the data set does not change. The measures derived at load time are filled in
-- here too (hour, flags); an open request has no resolution.
INSERT INTO fact_service_request
    (request_id, date_key, agency_key, complaint_key, location_key, channel_key, status_key,
     created_at, created_hour, closed_at, is_closed, resolution_hours, has_valid_resolution,
     closed_within_30d)
VALUES
    (@request_id@, 20260101, @agency@, @descriptor@, @location@, @channel@, @status@,
     TIMESTAMP '2026-01-01 12:00:00', 12, NULL, false, NULL, false, false);
