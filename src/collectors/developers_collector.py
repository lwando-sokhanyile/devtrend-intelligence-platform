"""
Developers Collector
====================
Fetches trending developers from GitHub API
and loads them into PostgreSQL.

Author: Lwando Sokhanyile
Project: DevTrend Intelligence Platform
"""

import requests
import psycopg2
import logging
import os
from datetime import date, datetime, timedelta
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
        logging.FileHandler("developers_collector.log")
    ]
)
log = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/search/users"
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"



def fetch_trending_developers():
    """
    Fetches developers who have been most active recently
    by searching for users with the most followers
    who joined in the last 30 days.
    Returns a list of developer dictionaries.
    """
    log.info("Fetching trending developers from GitHub API...")

    month_ago = (date.today() - timedelta(days=30)).isoformat()

    params = {
        "q": f"type:user created:>{month_ago} followers:>10",
        "sort": "followers",
        "order": "desc",
        "per_page": 25,
    }

    try:
        response = requests.get(
            GITHUB_API_URL,
            headers=HEADERS,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        users = response.json().get("items", [])
        log.info(f"Fetched {len(users)} trending developers.")

        # Enrich each user with their full profile
        developers = []
        for user in users:
            profile = fetch_user_profile(user["login"])
            if profile:
                developers.append(profile)

        log.info(f"Enriched {len(developers)} developer profiles.")
        return developers

    except requests.exceptions.Timeout:
        log.error("GitHub API request timed out.")
        raise

    except requests.exceptions.HTTPError as e:
        log.error(f"GitHub API error: {e.response.status_code} - {e.response.text}")
        raise

    except requests.exceptions.RequestException as e:
        log.error(f"Failed to connect to GitHub API: {e}")
        raise


def fetch_user_profile(username):
    """
    Fetches the full profile for a single GitHub user.
    Returns a dictionary with user details.
    """
    try:
        response = requests.get(
            f"https://api.github.com/users/{username}",
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        log.warning(f"Could not fetch profile for {username}: {e}")
        return None




def validate_developer(dev):
    """
    Checks that a developer record has all required fields.
    Returns True if valid, False if we should skip it.
    """
    required_fields = ["login", "followers"]

    for field in required_fields:
        if field not in dev or dev[field] is None:
            log.warning(f"Skipping developer — missing field: {field}")
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
    """Creates the raw_trending_developers table if it doesn't exist."""
    log.info("Creating table if it doesn't exist...")

    sql = """
        CREATE TABLE IF NOT EXISTS raw_trending_developers (
            id              SERIAL PRIMARY KEY,
            snapshot_date   DATE NOT NULL,
            username        VARCHAR(100) NOT NULL,
            display_name    VARCHAR(200),
            bio             TEXT,
            location        VARCHAR(200),
            language        VARCHAR(100),
            followers       INTEGER DEFAULT 0,
            public_repos    INTEGER DEFAULT 0,
            github_url      VARCHAR(300),
            fetched_at      TIMESTAMP NOT NULL,
            UNIQUE (username, snapshot_date)
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



def load_developers(conn, developers):
    """
    Inserts trending developers into PostgreSQL.
    Idempotent — safe to run multiple times.
    """
    log.info(f"Loading {len(developers)} developers into PostgreSQL...")

    sql = """
        INSERT INTO raw_trending_developers (
            snapshot_date,
            username,
            display_name,
            bio,
            location,
            language,
            followers,
            public_repos,
            github_url,
            fetched_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (username, snapshot_date)
        DO NOTHING;
    """

    today      = date.today()
    fetched_at = datetime.utcnow()
    inserted   = 0
    skipped    = 0

    for dev in developers:

        if not validate_developer(dev):
            skipped += 1
            continue

        values = (
            today,
            dev.get("login"),
            dev.get("name"),
            dev.get("bio"),
            dev.get("location"),
            dev.get("language"),  
            dev.get("followers", 0),
            dev.get("public_repos", 0),
            dev.get("html_url", ""),
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
            log.error(f"Failed to insert {dev.get('login')}: {e}")
            conn.rollback()
            skipped += 1

    log.info(f"Done — inserted: {inserted}, skipped: {skipped}")
    return inserted, skipped


def main():
    log.info("=" * 55)
    log.info("Developers Collector Starting")
    log.info("=" * 55)

    # Fetch developers
    developers = fetch_trending_developers()

    # Connect to database
    conn = get_db_connection()

    try:
        create_table(conn)
        inserted, skipped = load_developers(conn, developers)

    finally:
        conn.close()
        log.info("Database connection closed.")

    log.info("=" * 55)
    log.info(f"Developers Collector Finished — {inserted} inserted, {skipped} skipped")
    log.info("=" * 55)


if __name__ == "__main__":
    main()