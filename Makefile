.PHONY: lint install cover

# Install dependencies
install:
	pip install -r requirements.txt

# Run pylint on all Python files
lint:
	pylint $$(git ls-files '*.py') || true

# Run Pytest and display coverage report
cover:
	coverage run -m pytest && coverage report -m