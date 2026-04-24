.PHONY: run lint test build-mac clean

run:
	PYTHONPATH=src uv run python -m vibe_streamer.main

lint:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run pytest tests/

build-mac:
	uv run pyinstaller --name "Vibe Streamer" --windowed --noconfirm src/vibe_streamer/main.py

clean:
	rm -rf build/ dist/ *.spec .pytest_cache .ruff_cache .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
