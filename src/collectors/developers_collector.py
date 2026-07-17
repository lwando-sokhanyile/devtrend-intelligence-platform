import requests
import psycopg2
import logging
import os
import json
from datetime import date, datetime

 
# ── Load .env file ────────────────────────────────────────────────────────────
load_dotenv()
 
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DB_HOST      = os.getenv("DB_HOST", "localhost")
DB_PORT      = os.getenv("DB_PORT", "5432")
DB_NAME      = os.getenv("DB_NAME", "devtrend_db")
DB_USER      = os.getenv("DB_USER")
DB_PASSWORD  = os.getenv("DB_P

def validate_repo(repo):
    """
    Checks that a repo has all the fields we need.
    Returns True if valid, False if we should skip it.
    """
    required_fields = ["full_name", "name", "owner", "stargazers_count"]
 
    for field in required_fields:
        if field not in repo or repo[field] is None:
            log.warning(f"Skipping repo — missing field: {field}")
            return False
 
    return True
 
 
# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — DATABASE
# ══════════════════════════════════════════════════════════════════════════════
 
def get_db_connection():
    """Connects to PostgreSQL and returns the connection."""
    log.info(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        log.info("Connected to PostgreSQL.")
        return conn
    except psycopg2.OperationalError as e:
        log.error(f"Could not connect to PostgreSQL: {e}")
        raise
 
 
def create_table(conn):
    """Creates the raw_trending_repos table if it doesn't exist."""
    log.info("Creating table if it doesn't exist...")
 
    sql = """
        CREATE TABLE IF NOT EXISTS raw_trending_repos (
            id              SERIAL PRIMARY KEY,
            snapshot_date   DATE NOT NULL,
            repo_name       VARCHAR(200) NOT NULL,
            owner           VARCHAR(100) NOT NULL,
            description     TEXT,
            language        VARCHAR(100),
            stars_total     INTEGER DEFAULT 0,
            forks           INTEGER DEFAULT 0,
            topics          JSONB,
            github_url      VARCHAR(300),
            fetched_at      TIMESTAMP NOT NULL,
            UNIQUE (repo_name, owner, snapshot_date)
        );
    """
 
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        log.info("Table ready.")
    except psycopg2.Error as e:
        log.error(f"Failed to create table: {e}")
        conn.rollback()
        raise
 