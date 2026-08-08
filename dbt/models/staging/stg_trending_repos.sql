with source as (
    select * from {{ source('raw', 'raw_trending_repos') }}
),

cleaned as (
    select
        id,
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
    from source
    where repo_name is not null
      and owner is not null
      and snapshot_date is not null
)

select * from cleaned