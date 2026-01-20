# AI-First Architectural Design System (2025 Edition)

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### 🛠️ Infrastructure Setup
Start the core services (PostgreSQL, Redis, MinIO) and the Backend API:
```bash
cd infrastructure/docker
docker-compose up -d --build
```
The backend will automatically wait for the database, run migrations, seed initial data, and start the server.

### 🐍 Manual Backend Development
If you prefer running the backend locally without Docker for development:

1. **Setup Environment**
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   Create a `.env` file in the `backend/` directory:
   ```env
   PROJECT_NAME=ARchitectureAI
   API_V1_STR=/api/v1
   DATABASE_URL=postgresql://postgres:password@localhost:5432/architecture_ai
   REDIS_URL=redis://localhost:6379/0
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   OPENAI_API_KEY=your-api-key-here
   ```

3. **Run Migrations & Seed Data**
   ```bash
   # Ensure DB is running via Docker first
   alembic upgrade head
   python app/initial_data.py
   ```

4. **Start the API**
   ```bash
   uvicorn app.main:app --reload
   ```

### ⚛️ Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 🧪 Running Tests
**Flow Test (Mocked):**
```bash
cd backend
.\venv\Scripts\python tests/test_flow.py
```

**API Integration Tests:**
```bash
cd backend
.\venv\Scripts\python tests/test_api.py
```

## Executive Overview
A production-grade, AI-first architectural design system capable of converting natural language prompts into validated 2D floorplans, 3D models, and BIM-compliant IFC files.

## System Architecture
User Prompt → LLM Parser → Constraint Graph → Diffusion Model → Vector Floorplan → 3D Extrusion → IFC / GLB Export → Web Viewer

## Tech Stack
- **Backend**: Python 3.11, FastAPI, PostgreSQL + pgvector, Redis, Celery
- **AI/ML**: PyTorch, LangChain, OpenAI/Claude, Hugging Face
- **Geometry**: pythonOCC, Shapely, Trimesh, IfcOpenShell
- **Frontend**: React, Three.js, ThatOpen Engine

## Project Structure
- `/backend`: FastAPI application and core logic
- `/ml`: Machine learning pipelines (training, inference)
- `/infrastructure`: Docker and deployment configuration
- `/frontend`: Web application (React)
