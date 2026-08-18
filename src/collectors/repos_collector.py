"""
Repositories Collector
======================
Fetches trending repositories from the GitHub API
and loads them into PostgreSQL.
 
Author: Lwando Sokhanyile
Project: DevTrend Intelligence Platform
"""
 
import requests
import psycopg2
import logging
import os
import json
from datetime import date, datetime
from dotenv import load_dotenv
 

load_dotenv()
 
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DB_HOST      = os.getenv("DB_HOST", "localhost")
DB_PORT      = os.getenv("DB_PORT", "5432")
DB_NAME      = os.getenv("DB_NAME", "devtrend_db")
DB_USER      = os.getenv("DB_USER")
DB_PASSWORD  = os.getenv("DB_PASSWORD")
 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("repos_collector.log")
    ]
)
log = logging.getLogger(__name__)
 
# ── GitHub API ────────────────────────────────────────────────────────────────
# We search for repos created in the last 7 days with many stars
# This is the closest public API approach to "trending"
GITHUB_API_URL = "https://api.github.com/search/repositories"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"
 
 
 
def fetch_trending_repos():
    """
    Calls the GitHub Search API to get repositories
    sorted by stars, created in the last 7 days.
    Returns a list of repository dictionaries.
    """
    log.info("Fetching trending repositories from GitHub API...")
 
    # Search for repos created in the last 7 days, sorted by stars
    from datetime import timedelta
    week_ago = (date.today() - timedelta(days=7)).isoformat()
 
    params = {
        "q": f"created:>{week_ago}",
        "sort": "stars",
        "order": "desc",
        "per_page": 25,   # top 25 trending repos
    }
 
    try:
        response = requests.get(
            GITHUB_API_URL,
            headers=HEADERS,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        repos = data.get("items", [])
        log.info(f"Fetched {len(repos)} trending repositories.")
        return repos
 
    except requests.exceptions.Timeout:
        log.error("GitHub API request timed out.")
        raise
 
    except requests.exceptions.HTTPError as e:
        log.error(f"GitHub API error: {e.response.status_code} - {e.response.text}")
        raise
 
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to connect to GitHub API: {e}")
        raise


 
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




 
def load_repos(conn, repos):
    """
    Inserts trending repos into PostgreSQL.
    Uses ON CONFLICT DO NOTHING so running twice
    never creates duplicate rows (idempotent).
    """
    log.info(f"Loading {len(repos)} repos into PostgreSQL...")
 
    sql = """
        INSERT INTO raw_trending_repos (
            snapshot_date,
            repo_name,
            owner,
            description,
            language,
            stars_total,
            forks,
            topics,
            github_url,
            fetched_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (repo_name, owner, snapshot_date)
        DO NOTHING;
    """
 
    today      = date.today()
    fetched_at = datetime.utcnow()
    inserted   = 0
    skipped    = 0
 
    for repo in repos:
 
        # Validate before inserting
        if not validate_repo(repo):
            skipped += 1
            continue
 
        values = (
            today,
            repo["name"],
            repo["owner"]["login"],
            repo.get("description", ""),
            repo.get("language"),
            repo.get("stargazers_count", 0),
            repo.get("forks_count", 0),
            json.dumps(repo.get("topics", [])),
            repo.get("html_url", ""),
            fetched_at,
        )
 
        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                if cur.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1  # already exists for today
            conn.commit()
 
        except psycopg2.Error as e:
            log.error(f"Failed to insert {repo['name']}: {e}")
            conn.rollback()
            skipped += 1
 
    log.info(f"Done — inserted: {inserted}, skipped: {skipped}")
    return inserted, skipped
 

 
def main():
    log.info("=" * 55)
    log.info("Repos Collector Starting")
    log.info("=" * 55)
 
    # Fetch
    repos = fetch_trending_repos()
 
    # Connect to database
    conn = get_db_connection()
 
    try:
        # Create table if needed
        create_table(conn)
 
        # Load data
        inserted, skipped = load_repos(conn, repos)
 
    finally:
        conn.close()
        log.info("Database connection closed.")
 
    log.info("=" * 55)
    log.info(f"Repos Collector Finished — {inserted} inserted, {skipped} skipped")
    log.info("=" * 55)
 
 
if __name__ == "__main__":
    main()