.PHONY: check test lint types app
check: lint types test
test:
	uv run pytest -q
lint:
	uv run ruff check . && uv run ruff format --check .
types:
	uv run mypy
app:
	uv run streamlit run app.py
