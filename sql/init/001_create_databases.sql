SELECT 'CREATE DATABASE devtrend_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'devtrend_db')\gexec

SELECT 'CREATE DATABASE airflow_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow_db')\gexec

SELECT 'CREATE DATABASE metabase_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'metabase_db')\gexec