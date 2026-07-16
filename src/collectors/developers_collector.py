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