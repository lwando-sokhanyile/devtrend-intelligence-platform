with source as (
    select * from {{ source('raw', 'raw_trending_developers') }}
),

cleaned as (
    select
        id,
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
    from source
    where username is not null
      and snapshot_date is not null
)

select * from cleaned