run:
	docker-compose --profile metabase up -d postgres metabase

down:
	docker-compose down

collect:
	python src/collectors/repos_collector.py
	python src/collectors/languages_collector.py
	python src/collectors/developers_collector.py

transform:
	cd dbt && dbt run

test:
	cd dbt && dbt test

pipeline: collect transform test