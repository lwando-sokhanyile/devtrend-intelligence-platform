with repos as (
    select * from {{ ref('stg_trending_repos') }}
),

languages as (
    select * from {{ ref('stg_language_trends') }}
),

joined as (
    select
        r.id,
        r.snapshot_date,
        r.repo_name,
        r.owner,
        r.description,
        r.language,
        r.stars_total,
        r.forks,
        r.topics,
        r.github_url,
        r.fetched_at,
        l.rank          as language_rank,
        l.repo_count    as language_repo_count
    from repos r
    left join languages l
        on r.language = l.language
        and r.snapshot_date = l.snapshot_date
)

select * from joined