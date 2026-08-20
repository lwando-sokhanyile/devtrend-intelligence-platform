CREATE TABLE IF NOT EXISTS raw_trending_repos (
    id            SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    repo_name     VARCHAR(200) NOT NULL,
    owner         VARCHAR(100) NOT NULL,
    description   TEXT,
    language      VARCHAR(100),
    stars_total   INTEGER DEFAULT 0,
    forks         INTEGER DEFAULT 0,
    topics        JSONB,
    github_url    VARCHAR(300),
    fetched_at    TIMESTAMP NOT NULL,
    UNIQUE (repo_name, owner, snapshot_date)
);

CREATE TABLE IF NOT EXISTS raw_language_trends (
    id            SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    language      VARCHAR(100) NOT NULL,
    repo_count    INTEGER NOT NULL,
    rank          INTEGER NOT NULL,
    fetched_at    TIMESTAMP NOT NULL,
    UNIQUE (language, snapshot_date)
);

CREATE TABLE IF NOT EXISTS raw_trending_developers (
    id            SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    username      VARCHAR(100) NOT NULL,
    display_name  VARCHAR(200),
    bio           TEXT,
    location      VARCHAR(200),
    language      VARCHAR(100),
    followers     INTEGER DEFAULT 0,
    public_repos  INTEGER DEFAULT 0,
    github_url    VARCHAR(300),
    fetched_at    TIMESTAMP NOT NULL,
    UNIQUE (username, snapshot_date)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id             SERIAL PRIMARY KEY,
    collector_name VARCHAR(100),
    started_at     TIMESTAMP,
    finished_at    TIMESTAMP,
    records_fetched INTEGER,
    records_inserted INTEGER,
    records_skipped INTEGER,
    status         VARCHAR(20),
    error_message  TEXT
);