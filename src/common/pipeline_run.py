"""
Pipeline Run Logger
Logs every collector run to the pipeline_runs table.
"""

import logging
from datetime import datetime
from src.common.database import get_connection

log = logging.getLogger(__name__)


def log_pipeline_run(collector_name, started_at, records_fetched,
                     records_inserted, records_skipped, status, error_message=None):
    """Writes a pipeline run record to the pipeline_runs table."""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pipeline_runs
                    (collector_name, started_at, finished_at, records_fetched,
                     records_inserted, records_skipped, status, error_message)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                collector_name, started_at, datetime.utcnow(),
                records_fetched, records_inserted, records_skipped,
                status, error_message
            ))
        conn.commit()
        conn.close()
        log.info(f"Pipeline run logged for {collector_name}.")
    except Exception as e:
        log.error(f"Failed to log pipeline run: {e}")