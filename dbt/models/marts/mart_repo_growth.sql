with growth as (
    select * from {{ ref('int_repo_daily_growth') }}
)

select
    snapshot_date,
    repo_name,
    owner,
    language,
    stars_total,
    stars_gained,
    rank() over (
        partition by snapshot_date
        order by stars_gained desc
    ) as growth_rank
from growth
where stars_gained > 0
order by snapshot_date desc, stars_gained desc