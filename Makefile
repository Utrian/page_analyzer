init:
	poetry init
	poetry config virtualenvs.in-project true
	poetry shell
	poetry add pytest pytest-cov coverage flake8
	curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-0.10.4-linux-amd64 > ./test-coverage-tool #бинарник для работы test_coverage на linux
	chmod +x ./test-coverage-tool
	./test-coverage-tool before-build
	poetry run pytest --cov=main_dir --cov-report xml
	./test-coverage-tool after-build -r #id
	printf ".pytest_cache \n\n.venv \n\n.vscode \n\ndist \n\n__pychache__ \n\n.coverage \n" > .gitignore

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
