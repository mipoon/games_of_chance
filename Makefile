.PHONY: lint install

# Install dependencies
install:
	pip install -r requirements.txt

# Run pylint on all Python files
lint:
	pylint $$(git ls-files '*.py') || true
