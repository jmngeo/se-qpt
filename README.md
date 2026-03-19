# SE-QPT: Systems Engineering Qualification Planning Tool

## Overview

This thesis presents the development of a Systems Engineering Qualification Planning Tool - a GenAI-powered web platform that enables organizations to systematically plan Systems Engineering qualifications. The tool integrates maturity assessment, AI-enhanced role mapping, and RAG-based learning objective generation to bridge the gap between SE competency frameworks and practical qualification implementation.

The tool guides organizations through a structured four-phase process:

1. **Phase 1 – Prepare SE Training**: Assess organizational maturity and identify SE roles based on job tasks
2. **Phase 2 – Identify Requirements and Competencies**: Identify required competency levels through expert and self-assessments
3. **Phase 3 – Macro Planning**: Create a macro-level training plan with learning formats and scheduling
4. **Phase 4 – Micro Planning**: Develop detailed micro-level implementation plans

## Technology Stack

### Backend
- **Framework**: Flask 3.0 (Python)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0 + Flask-Migrate
- **Auth**: Flask-JWT-Extended
- **AI/ML**: LangChain + OpenAI GPT-4 for role mapping and learning objective generation
- **Vector Search**: FAISS for competency vector matching
- **RAG**: ChromaDB for context-aware learning objective retrieval

### Frontend
- **Framework**: Vue 3 (Composition API)
- **UI Library**: Element Plus
- **State Management**: Pinia
- **Charts**: ECharts (vue-echarts), Chart.js
- **Export**: jsPDF + xlsx
- **Build Tool**: Vite

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (reverse proxy + static file serving)

## Quick Start

### Option A: Docker (Recommended)

```bash
git clone <repository-url>
cd SE-QPT-Master-Thesis

# Create environment file
cp .env.example .env
# Edit .env — set OPENAI_API_KEY and a strong SECRET_KEY

# Start all services
docker compose up --build -d

# Initialize the database (first time only)
docker exec seqpt-backend python setup/core/init_db_as_postgres.py
docker exec seqpt-backend python setup/populate/populate_competencies.py
docker exec seqpt-backend python setup/populate/populate_iso_processes.py
docker exec seqpt-backend python setup/populate/populate_roles_and_matrices.py
docker exec seqpt-backend python setup/populate/populate_process_competency_matrix.py
docker exec seqpt-backend python setup/database_objects/create_stored_procedures.py
```

Application is available at `http://localhost`.

### Option B: Manual Setup

#### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Node.js 18+

#### 1. Database Setup

```bash
psql -U postgres -c "CREATE USER seqpt_admin WITH PASSWORD 'your_password';"
psql -U postgres -c "CREATE DATABASE seqpt_database OWNER seqpt_admin;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE seqpt_database TO seqpt_admin;"
```

#### 2. Backend Setup

```bash
cd src/backend

python -m venv ../../venv
# Windows:
../../venv/Scripts/activate
# Linux/Mac:
# source ../../venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY
```

#### 3. Initialize Database

```bash
# Run in order from src/backend/
python setup/core/init_db_as_postgres.py
python setup/populate/populate_competencies.py
python setup/populate/populate_iso_processes.py
python setup/populate/populate_roles_and_matrices.py
python setup/populate/populate_process_competency_matrix.py
python setup/database_objects/create_stored_procedures.py
```

#### 4. Frontend Setup

```bash
cd src/frontend
npm install
```

#### 5. Run

```bash
# Terminal 1 — Backend (http://localhost:5000)
cd src/backend
python run.py

# Terminal 2 — Frontend (http://localhost:3000)
cd src/frontend
npm run dev
```

## Project Structure

```
SE-QPT-Master-Thesis/
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── routes/          # API route blueprints
│   │   │   ├── services/        # Business logic
│   │   │   └── utils/           # Helpers and utilities
│   │   ├── config/              # App configuration
│   │   ├── data/                # Static data (PMT examples, templates)
│   │   ├── migrations/          # Alembic DB migrations
│   │   ├── setup/               # Database initialization scripts
│   │   │   ├── core/            # DB creation and schema init
│   │   │   ├── populate/        # Reference data population
│   │   │   ├── database_objects/# Stored procedures and triggers
│   │   │   └── ui_data/         # UI-specific seed data
│   │   ├── tests/               # Backend test suite
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── run.py               # Application entry point
│   │   └── requirements.txt     # Python dependencies
│   │
│   └── frontend/
│       ├── src/
│       │   ├── views/           # Page components (phases, plans, admin)
│       │   ├── components/      # Reusable UI components
│       │   ├── stores/          # Pinia state stores
│       │   ├── api/             # Axios API client
│       │   └── router/          # Vue Router configuration
│       ├── package.json
│       └── vite.config.js
│
├── docker-compose.yml           # Production container orchestration
├── .env.example                 # Environment variable template
└── README.md
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
POSTGRES_USER=seqpt_admin
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=seqpt_database

# Flask
FLASK_ENV=production
SECRET_KEY=your_secret_key_here

# OpenAI (required for LLM features)
OPENAI_API_KEY=sk-your-openai-api-key-here
```

For local development, the backend also reads `src/backend/.env`:

```bash
DATABASE_URL=postgresql://seqpt_admin:your_password@localhost:5432/seqpt_database
FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## Database Schema

### Core Reference Tables
- `organization` — Multi-tenant organizations
- `competency` / `competency_indicators` — SE competency definitions
- `iso_system_life_cycle_processes` / `iso_processes` — ISO 15288 process hierarchy
- `role_cluster` — Standard SE role definitions

### Matrix Tables
- `role_process_matrix` — Role-to-process involvement levels (per org)
- `process_competency_matrix` — Process-to-competency requirements (global)
- `role_competency_matrix` — Calculated required proficiency per role
- `unknown_role_process_matrix` / `unknown_role_competency_matrix` — For task-based custom roles

### Assessment & Planning Tables
- `users` — User accounts
- `user_role_cluster` — Identified role per user
- `user_se_competency_survey_results` — Phase 2 assessment results
- `user_assessment` — Assessment records
- `learning_strategy` / `strategy_template` — Training strategy definitions
- `generated_learning_objectives` — AI-generated LOs per user
- `organization_existing_trainings` — Org-provided training catalogue

## Production Deployment

The application is containerized and runs on Docker. The `docker-compose.yml` defines three services: `db` (PostgreSQL), `backend` (Flask), and `frontend` (Nginx + Vue build).

```bash
# Deploy
docker compose up --build -d

# View logs
docker compose logs -f

# Check status
docker compose ps
```

Nginx proxies all `/api/` requests to the Flask backend; all other requests serve the Vue SPA.

## License

This project is developed as part of a Master's thesis at Paderborn university, Germany.

## Author

Jomon George
