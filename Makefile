# Agentic Workbench - LangGraph
# Convenient commands for development and deployment

.PHONY: help setup setup-all setup-backend setup-frontend start start-backend start-frontend stop clean logs test health-check

# Default target
help:
	@echo "Agentic Workbench (LangGraph) - Available commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup, setup-all    Setup both backend and frontend services"
	@echo "  setup-backend       Setup only the backend service"  
	@echo "  setup-frontend      Setup only the frontend service"
	@echo ""
	@echo "Start/Stop Commands:"
	@echo "  start               Start both services in detached mode"
	@echo "  start-backend       Start only the backend service"
	@echo "  start-frontend      Start only the frontend service"
	@echo "  stop                Stop all running services"
	@echo ""
	@echo "Development Commands:"
	@echo "  logs                Show logs from all services"
	@echo "  logs-backend        Show logs from backend service only"
	@echo "  logs-frontend       Show logs from frontend service only"
	@echo "  health-check        Check if services are running properly"
	@echo "  test                Run basic connectivity tests"
	@echo ""
	@echo "Cleanup Commands:"
	@echo "  clean               Stop and remove containers, networks, and volumes"
	@echo "  clean-hard          Clean + remove images"

# Setup commands
setup: setup-all
setup-all:
	@echo "🔧 Setting up Agentic Workbench (LangGraph)..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env and add your OPENROUTER_API_KEY"; \
	else \
		echo "✅ .env file already exists"; \
	fi
	@echo "🐳 Building Docker images..."
	@docker compose build
	@echo "✅ Setup complete! Run 'make start' to begin."

setup-backend:
	@echo "🔧 Setting up backend service..."
	@docker compose build backend
	@echo "✅ Backend setup complete!"

setup-frontend:
	@echo "🔧 Setting up frontend service..."
	@docker compose build frontend
	@echo "✅ Frontend setup complete!"

# Start/Stop commands
start:
	@echo "🚀 Starting Agentic Workbench (LangGraph)..."
	@docker compose up -d
	@echo "✅ Services started!"
	@echo ""
	@echo "🌐 Access points:"
	@echo "  - OpenWebUI Interface: http://localhost:3000"
	@echo "  - API Documentation:   http://localhost:8000/docs"
	@echo "  - API Health Check:    http://localhost:8000/v1/"
	@echo ""
	@echo "📊 Check status with: make health-check"
	@echo "📝 View logs with:    make logs"

start-backend:
	@echo "🚀 Starting backend service..."
	@docker compose up -d backend
	@echo "✅ Backend started on http://localhost:8000"

start-frontend:
	@echo "🚀 Starting frontend service..."
	@docker compose up -d frontend
	@echo "✅ Frontend started on http://localhost:3000"

stop:
	@echo "🛑 Stopping all services..."
	@docker compose down
	@echo "✅ All services stopped."

# Development commands
logs:
	@docker compose logs -f

logs-backend:
	@docker compose logs -f backend

logs-frontend:
	@docker compose logs -f frontend

health-check:
	@echo "🏥 Checking service health..."
	@echo ""
	@echo "📊 Docker Compose Status:"
	@docker compose ps
	@echo ""
	@echo "🔍 Backend API Health:"
	@curl -s http://localhost:8000/v1/ | jq -r '.name // "❌ Backend not responding"' || echo "❌ Backend not responding"
	@echo ""
	@echo "🔍 Available Models:"
	@curl -s http://localhost:8000/v1/models | jq -r '.data[].id // "❌ No models available"' || echo "❌ Backend not responding"

test:
	@echo "🧪 Running basic connectivity tests..."
	@echo ""
	@echo "Testing backend API..."
	@curl -s -f http://localhost:8000/v1/ > /dev/null && echo "✅ Backend API is responding" || echo "❌ Backend API is not responding"
	@echo ""
	@echo "Testing model endpoint..."
	@curl -s -f http://localhost:8000/v1/models > /dev/null && echo "✅ Models endpoint is working" || echo "❌ Models endpoint is not working"
	@echo ""
	@echo "Testing frontend..."
	@curl -s -f http://localhost:3000 > /dev/null && echo "✅ Frontend is responding" || echo "❌ Frontend is not responding"

# Cleanup commands
clean:
	@echo "🧹 Cleaning up containers, networks, and volumes..."
	@docker compose down -v --remove-orphans
	@echo "✅ Cleanup complete."

clean-hard: clean
	@echo "🧹 Removing Docker images..."
	@docker compose down --rmi all -v --remove-orphans
	@echo "✅ Hard cleanup complete."

# Development helpers
dev-backend:
	@echo "🔧 Running backend in development mode..."
	@cd backend && python main.py

install-backend-deps:
	@echo "📦 Installing backend dependencies..."
	@cd backend && pip install -r requirements.txt

# Quick commands for common workflows
rebuild:
	@echo "🔄 Rebuilding and restarting services..."
	@docker compose down
	@docker compose build
	@docker compose up -d
	@make health-check