with developers as (
    select * from {{ ref('int_developer_activity') }}
)

select
    snapshot_date,
    username,
    display_name,
    bio,
    location,
    language,
    followers,
    public_repos,
    github_url,
    daily_rank
from developers
order by snapshot_date desc, daily_rank asc