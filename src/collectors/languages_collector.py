import requests
import psycopg2
import logging
import json
from collections import Counter
from datetime import date, datetime, timedelta
from src.common.config import (
    GITHUB_TOKEN, DB_HOST, DB_PORT,
    DB_NAME, DB_USER, DB_PASSWORD
)
from src.common.logging_config import setup_logging
from src.common.pipeline_run import log_pipeline_run

log_pipeline_run(
    collector_name="repos_collector",
    started_at=started_at,
    records_fetched=len(repos),
    records_inserted=inserted,
    records_skipped=skipped,
    status="success"
)

log = setup_logging(__name__)

GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"



def fetch_language_trends():
    """
    Fetches trending repos from the last 7 days,
    then counts how many trending repos use each language.
    Returns a list of dicts: {language, repo_count, rank}
    """
    log.info("Fetching language trends from GitHub API...")

    week_ago = (date.today() - timedelta(days=7)).isoformat()

    params = {
        "q": f"created:>{week_ago}",
        "sort": "stars",
        "order": "desc",
        "per_page": 100,  
    }

    try:
        response = requests.get(
            GITHUB_API_URL,
            headers=HEADERS,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        repos = response.json().get("items", [])
        log.info(f"Fetched {len(repos)} repos to analyse language distribution.")

        
        languages = [
            repo["language"]
            for repo in repos
            if repo.get("language") 
        ]

        language_counts = Counter(languages)

        results = []
        for rank, (language, count) in enumerate(language_counts.most_common(), start=1):
            results.append({
                "language":   language,
                "repo_count": count,
                "rank":       rank,
            })

        log.info(f"Found {len(results)} languages in trending repos.")
        return results

    except requests.exceptions.Timeout:
        log.error("GitHub API request timed out.")
        raise

    except requests.exceptions.HTTPError as e:
        log.error(f"GitHub API error: {e.response.status_code} - {e.response.text}")
        raise

    except requests.exceptions.RequestException as e:
        log.error(f"Failed to connect to GitHub API: {e}")
        raise



def validate_language(record):
    """
    Checks that a language record has all required fields.
    Returns True if valid, False if we should skip it.
    """
    if not record.get("language"):
        log.warning("Skipping record — missing language name.")
        return False

    if not isinstance(record.get("repo_count"), int):
        log.warning(f"Skipping {record.get('language')} — invalid repo_count.")
        return False

    return True



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
    """Creates the raw_language_trends table if it doesn't exist."""
    log.info("Creating table if it doesn't exist...")

    sql = """
        CREATE TABLE IF NOT EXISTS raw_language_trends (
            id              SERIAL PRIMARY KEY,
            snapshot_date   DATE NOT NULL,
            language        VARCHAR(100) NOT NULL,
            repo_count      INTEGER NOT NULL,
            rank            INTEGER NOT NULL,
            fetched_at      TIMESTAMP NOT NULL,
            UNIQUE (language, snapshot_date)
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


def load_language_trends(conn, records):
    """
    Inserts language trend records into PostgreSQL.
    Idempotent — safe to run multiple times.
    """
    log.info(f"Loading {len(records)} language records into PostgreSQL...")

    sql = """
        INSERT INTO raw_language_trends (
            snapshot_date,
            language,
            repo_count,
            rank,
            fetched_at
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (language, snapshot_date)
        DO NOTHING;
    """

    today      = date.today()
    fetched_at = datetime.utcnow()
    inserted   = 0
    skipped    = 0

    for record in records:

        if not validate_language(record):
            skipped += 1
            continue

        values = (
            today,
            record["language"],
            record["repo_count"],
            record["rank"],
            fetched_at,
        )

        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                if cur.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            conn.commit()

        except psycopg2.Error as e:
            log.error(f"Failed to insert {record['language']}: {e}")
            conn.rollback()
            skipped += 1

    log.info(f"Done — inserted: {inserted}, skipped: {skipped}")
    return inserted, skipped



def main():
    log.info("=" * 55)
    log.info("Languages Collector Starting")
    log.info("=" * 55)

    records = fetch_language_trends()

    conn = get_db_connection()

    try:
        create_table(conn)
        inserted, skipped = load_language_trends(conn, records)

    finally:
        conn.close()
        log.info("Database connection closed.")

    log.info("=" * 55)
    log.info(f"Languages Collector Finished — {inserted} inserted, {skipped} skipped")
    log.info("=" * 55)


if __name__ == "__main__":
    main()