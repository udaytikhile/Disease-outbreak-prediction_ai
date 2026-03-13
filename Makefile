.PHONY: dev server client install clean check

# ─── Start both servers ───────────────────────────
dev:
	@echo "🚀 Starting dev environment..."
	@make server & make client

# ─── Backend ──────────────────────────────────────
server:
	@echo "🐍 Starting Flask server..."
	cd server && python app.py

# ─── Frontend ─────────────────────────────────────
client:
	@echo "⚛️  Starting React dev server..."
	cd client && npm run dev

# ─── Install all dependencies ─────────────────────
install:
	@echo "📦 Installing dependencies..."
	pip install -r server/requirements.txt
	cd client && npm install

# ─── Clean build artifacts ────────────────────────
clean:
	@echo "🧹 Cleaning..."
	rm -rf client/dist client/node_modules
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete"

# ─── Run all checks (one command) ──────────────────
check:
	@echo "🧪 Running backend tests..."
	cd server && pytest
	@echo "🧪 Running frontend lint..."
	cd client && npm run lint
	@echo "✅ All checks finished"
