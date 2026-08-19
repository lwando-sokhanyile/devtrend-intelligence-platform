with languages as (
    select * from {{ ref('stg_language_trends') }}
),

ranked as (
    select
        snapshot_date,
        language,
        repo_count,
        rank,
        avg(repo_count) over (
            partition by language
            order by snapshot_date
            rows between 6 preceding and current row
        ) as avg_7_day_repo_count,
        avg(repo_count) over (
            partition by language
            order by snapshot_date
            rows between 29 preceding and current row
        ) as avg_30_day_repo_count
    from languages
)

select * from ranked
order by snapshot_date desc, rank asc