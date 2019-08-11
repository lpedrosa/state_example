install:
	@pipenv install --dev

run:
	@FLASK_APP=app.py FLASK_ENV=development pipenv run flask run -p 3000

lint:
	@pipenv run flake8

.PHONY: install run lint

