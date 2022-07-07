.PHONY: clean lint test

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

lint:
	poetry run black src tests
	poetry run flake8
	poetry run pylint src tests
