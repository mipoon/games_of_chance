.PHONY: install lint cover

# Install dependencies
install:
	pip install -r requirements.txt

# Run pylint on all Python files
PYTHON_FILES := $(shell find . -name "*.py" -not -path "./.venv/*")
lint:
	pylint $(PYTHON_FILES)

# Run Pytest and display coverage report
cover:
	coverage run -m pytest && coverage report -m