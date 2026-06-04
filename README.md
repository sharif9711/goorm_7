# YouTube Trend Research Agent

AI 기반 YouTube 트렌드 리서치 멀티 에이전트 SaaS 플랫폼입니다.

## Tech Stack

| Layer | Stack |
|-------|-------|
| Frontend | React 19, TypeScript, Vite, Ant Design, TanStack Query, Zustand, Recharts, Framer Motion |
| Backend | FastAPI, Python 3.12, SQLAlchemy, Celery, Redis |
| Database | PostgreSQL + pgvector |
| AI | OpenAI GPT-4o, Embeddings, Vision |

## Architecture

```
Frontend → FastAPI → LangGraph Workflow → Agent Nodes → Tools/Memory → PostgreSQL → GPT → Report
```

### LangGraph Workflow Graph

```
START → planner → collector → analysis → insights → critic
                                              ↓
                                    [quality < 70 or full/competitor?]
                                              ↓
                                    human_review (HITL interrupt)
                                              ↓
                                    report → evaluation → END
```

### Advanced Agent Features

| Feature | Implementation |
|---------|----------------|
| **Workflow Graph** | LangGraph `StateGraph` with conditional routing |
| **Tool Calling** | OpenAI function calling (`search_youtube_videos`, `get_channel_info`, etc.) |
| **Agent Memory** | Redis-backed per-user analysis history |
| **Human-in-the-Loop** | LangGraph `interrupt()` + `POST /api/analyze/{id}/resume` |
| **Agent Evaluation** | Post-hoc quality, coverage, hallucination scoring |

### Multi-Agent Pipeline

- **Planner Agent** — 작업 계획 생성
- **Trend Collector Agent** — YouTube Data API 수집
- **Channel Intelligence Agent** — 채널 성장률 분석
- **Keyword Intelligence Agent** — 키워드 트렌드 분석
- **Title Pattern Agent** — 제목 패턴 분석
- **Thumbnail Vision Agent** — Vision 썸네일 분석
- **Competitor Agent** — Gap Analysis
- **Insight Generator Agent** — GPT 인사이트 생성
- **Critic Agent** — 품질 검증
- **Report Agent** — Markdown/PDF 리포트 생성

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.12+
- YouTube Data API Key
- OpenAI API Key

### 1. Environment Setup

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit .env files with your API keys
```

### 2. Docker (Recommended)

```bash
docker compose up -d
```

### 3. Manual Setup

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Celery (separate terminals):**

```bash
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### 4. Access

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/trends` | Dashboard overview |
| GET | `/api/videos` | Video list |
| GET | `/api/channels` | Channel list |
| GET | `/api/keywords` | Keyword list |
| POST | `/api/analyze` | Run analysis |
| GET | `/api/analyze/{task_id}` | Get analysis result |
| POST | `/api/analyze/{task_id}/resume` | Human-in-the-loop resume |
| GET | `/api/workflow/{task_id}` | Workflow graph status |
| POST | `/api/reports` | Create report |
| GET | `/api/reports` | List reports |
| GET | `/api/reports/{id}` | Get report |
| GET | `/api/reports/{id}/pdf` | Download PDF |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── graph/           # LangGraph workflow, tools, state
│   │   ├── agents/          # Multi-agent modules
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/            # Config, auth, database
│   │   ├── models/          # SQLAlchemy models
│   │   ├── orchestrator/    # Agent orchestrator
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── workers/         # Celery tasks
│   ├── alembic/             # DB migrations
│   └── tests/
├── frontend/
│   └── src/
│       ├── api/             # API client
│       ├── components/      # Shared components
│       ├── features/        # Feature-based pages
│       ├── stores/          # Zustand stores
│       └── types/           # TypeScript types
└── docker-compose.yml
```

## Features

1. **Keyword Search** — YouTube 검색 + GPT 트렌드 리포트
2. **Trending Video Analysis** — 24h/7d/30d 급상승 분석
3. **Channel Growth Analysis** — 성장률, 업로드 빈도
4. **Competitor Analysis** — Gap Analysis + 비교 차트
5. **Title Pattern Analysis** — 클릭 유도 패턴
6. **Thumbnail Analysis** — Vision AI 스타일 분석
7. **Content Idea Generator** — 쇼츠/롱폼/블로그 아이디어
8. **Weekly Trend Report** — 매주 월요일 자동 생성 (Celery Beat)

## Testing

```bash
cd backend
pytest tests/ -v
```

## Deployment

| 구성요소 | 서비스 | 문서 |
|---------|--------|------|
| Frontend | [Vercel](https://vercel.com) | https://frontend-nu-five-48.vercel.app |
| Backend | Docker | [backend/DEPLOY.md](backend/DEPLOY.md) |
| Database | [Supabase](https://supabase.com) PostgreSQL + pgvector | [backend/DEPLOY.md](backend/DEPLOY.md) |

### 빠른 시작 (Production)

1. **Supabase** — PostgreSQL 프로젝트 생성 + `CREATE EXTENSION vector`
2. **Backend** — Docker로 배포 (VPS / Render 등), Supabase `DATABASE_URL` 설정
3. **Vercel** — `VITE_API_URL=https://your-backend-url/api` 설정 후 Redeploy

```bash
# 로컬 전체 스택
docker compose up -d

# Production (Supabase DB + Backend만)
docker compose -f docker-compose.prod.yml up -d
```

자세한 단계: **[backend/DEPLOY.md](backend/DEPLOY.md)**

## License

MIT
