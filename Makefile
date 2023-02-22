install:
	poetry install

build:
	poetry build

publish:
	poetry publish --dry-run

lint:
	poetry run flake8 page_analyzer

pytest:
	poetry run pytest
	poetry run pytest --cov=page_analyzer --cov-report xml
	poetry run pytest --cov-report term-missing --cov=page_analyzer

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
