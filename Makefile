.PHONY: dev server client install clean

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
	cd server && pip install -r requirements.txt
	cd client && npm install

# ─── Clean build artifacts ────────────────────────
clean:
	@echo "🧹 Cleaning..."
	rm -rf client/dist client/node_modules
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete"
