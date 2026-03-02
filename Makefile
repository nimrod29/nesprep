.PHONY: run run-backend run-frontend install install-backend install-frontend clean

# Run both backend and frontend
run:
	@echo "Starting backend and frontend..."
	@make run-backend & make run-frontend

# Run backend (REST API + WebSocket)
run-backend:
	@echo "Starting backend on http://localhost:8000"
	uv run uvicorn app.api.main:app --reload --port 8000

# Run frontend
run-frontend:
	@echo "Starting frontend on http://localhost:5173"
	cd frontend && npm run dev

# Install all dependencies
install: install-backend install-frontend

# Install backend dependencies
install-backend:
	uv sync

# Install frontend dependencies
install-frontend:
	cd frontend && npm install

# Clean build artifacts
clean:
	rm -rf frontend/node_modules frontend/dist
	rm -rf __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Run tests
test:
	uv run pytest

# Type check frontend
type-check:
	cd frontend && npm run type-check

# Lint frontend
lint:
	cd frontend && npm run lint
