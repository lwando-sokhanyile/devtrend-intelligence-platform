select *
from {{ ref('stg_language_trends') }}
where repo_count < 0