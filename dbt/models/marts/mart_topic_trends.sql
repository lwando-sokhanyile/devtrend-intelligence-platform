with repos as (
    select
        snapshot_date,
        repo_name,
        jsonb_array_elements_text(topics) as topic
    from {{ ref('stg_trending_repos') }}
    where topics is not null
      and jsonb_array_length(topics) > 0
),

counted as (
    select
        snapshot_date,
        topic,
        count(*) as repo_count
    from repos
    group by snapshot_date, topic
)

select
    snapshot_date,
    topic,
    repo_count,
    rank() over (
        partition by snapshot_date
        order by repo_count desc
    ) as topic_rank
from counted
order by snapshot_date desc, repo_count desc