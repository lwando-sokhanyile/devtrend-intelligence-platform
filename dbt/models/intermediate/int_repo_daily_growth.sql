with repos as (
    select * from {{ ref('stg_trending_repos') }}
),

growth as (
    select
        repo_name,
        owner,
        language,
        snapshot_date,
        stars_total,
        lag(stars_total) over (
            partition by repo_name, owner
            order by snapshot_date
        ) as prev_stars,
        stars_total - lag(stars_total) over (
            partition by repo_name, owner
            order by snapshot_date
        ) as stars_gained
    from repos
)

select
    repo_name,
    owner,
    language,
    snapshot_date,
    stars_total,
    prev_stars,
    coalesce(stars_gained, 0) as stars_gained
from growth
