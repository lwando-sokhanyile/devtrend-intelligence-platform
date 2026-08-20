import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = int(os.getenv("DB_PORT", 5433))
DB_NAME     = os.getenv("DB_NAME", "devtrend_db")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")