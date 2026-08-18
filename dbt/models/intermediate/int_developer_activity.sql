with developers as (
    select * from {{ ref('stg_trending_developers') }}
),

enriched as (
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
        fetched_at,
        rank() over (
            partition by snapshot_date
            order by followers desc
        ) as daily_rank
    from developers
)

select * from enriched