# 🍊 **POMEGRANATE** - AI-Powered Job Platform

> *Connecting talent with opportunity through intelligent AI matching*

## 🚀 **Quick Start**

### Prerequisites
- Docker Desktop
- Python 3.11+
- Node.js 18+
- Poetry (Python package manager)
- Git

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd pomegranate

# Start all services
docker-compose up -d

# Install backend dependencies
cd backend
poetry install
poetry run alembic upgrade head

# Install frontend dependencies
cd ../frontend
npm install

# Start development servers
# Backend (in one terminal)
cd backend && poetry run uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend && npm run dev
```

## 🏗️ **Architecture**

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL + Redis + ChromaDB
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **AI**: Google Gemini AI + Vector Embeddings
- **Infrastructure**: Docker + AWS (ECS, RDS, ElastiCache)

## 📁 **Project Structure**

```
pomegranate/
├── backend/                 # FastAPI backend
├── frontend/               # Next.js frontend
├── infrastructure/         # Terraform & Docker configs
├── docs/                  # Documentation
└── docker-compose.yml     # Local development
```

## 🔗 **Services**

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Database**: PostgreSQL on localhost:5432
- **Redis**: localhost:6379
- **ChromaDB**: localhost:8000

## 📋 **Development Tasks**

This project follows a 12-week development plan with 75 tasks. See `docs/DEVELOPMENT_PLAN.md` for complete details.

## 🤝 **Contributing**

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details
