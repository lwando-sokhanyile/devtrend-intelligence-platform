with source as (
    select * from {{ source('raw', 'raw_language_trends') }}
),

cleaned as (
    select
        id,
        snapshot_date,
        language,
        repo_count,
        rank,
        fetched_at
    from source
    where language is not null
      and snapshot_date is not null
)

select * from cleaned