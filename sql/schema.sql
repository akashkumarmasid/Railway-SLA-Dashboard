CREATE TABLE IF NOT EXISTS trains (
    train_id                TEXT PRIMARY KEY,
    train_name              TEXT NOT NULL,
    train_type              TEXT NOT NULL,
    zone                    TEXT NOT NULL,
    division                TEXT NOT NULL,
    origin                  TEXT NOT NULL,
    destination             TEXT NOT NULL,
    scheduled_duration_mins INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS trips (
    trip_id             TEXT PRIMARY KEY,
    train_id            TEXT NOT NULL REFERENCES trains(train_id),
    trip_date           TEXT NOT NULL,
    scheduled_departure TEXT NOT NULL,
    actual_departure    TEXT NOT NULL,
    scheduled_arrival   TEXT NOT NULL,
    actual_arrival      TEXT NOT NULL,
    delay_mins          REAL NOT NULL,
    sla_threshold_mins  INTEGER NOT NULL,
    breached            INTEGER NOT NULL CHECK (breached IN (0, 1))
);

CREATE TABLE IF NOT EXISTS complaints (
    complaint_id     TEXT PRIMARY KEY,
    train_id         TEXT NOT NULL REFERENCES trains(train_id),
    zone             TEXT NOT NULL,
    category         TEXT NOT NULL,
    filed_date       TEXT NOT NULL,
    resolved_date    TEXT NOT NULL,
    sla_target_days  INTEGER NOT NULL,
    resolved_in_days INTEGER NOT NULL,
    met_sla          INTEGER NOT NULL CHECK (met_sla IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_trips_train_id ON trips(train_id);
CREATE INDEX IF NOT EXISTS idx_trips_trip_date ON trips(trip_date);
CREATE INDEX IF NOT EXISTS idx_complaints_zone ON complaints(zone);
CREATE INDEX IF NOT EXISTS idx_complaints_filed_date ON complaints(filed_date);
