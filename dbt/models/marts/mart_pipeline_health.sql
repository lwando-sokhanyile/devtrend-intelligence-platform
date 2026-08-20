with runs as (
    select * from {{ source('raw', 'pipeline_runs') }}
)

select
    collector_name,
    started_at,
    finished_at,
    records_fetched,
    records_inserted,
    records_skipped,
    status,
    error_message,
    extract(epoch from (finished_at - started_at)) as duration_seconds
from runs
order by started_at desc