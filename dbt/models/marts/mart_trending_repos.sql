with repos as (
    select * from {{ ref('int_repos_with_language_rank') }}
)

select
    snapshot_date,
    repo_name,
    owner,
    description,
    language,
    stars_total,
    forks,
    topics,
    github_url,
    language_rank,
    language_repo_count,
    rank() over (
        partition by snapshot_date
        order by stars_total desc
    ) as daily_rank
from repos
order by snapshot_date desc, stars_total desc