# Backend Deployment (Supabase + Docker)

Railway 없이 배포하는 방법입니다.

## 아키텍처

```
Vercel (Frontend)  →  Docker Backend  →  Supabase PostgreSQL
                           ↓
                      Redis (선택)
```

| 구성요소 | 서비스 |
|---------|--------|
| Frontend | [Vercel](https://vercel.com) |
| Backend | Docker (`backend/Dockerfile`) |
| Database | [Supabase](https://supabase.com) PostgreSQL + pgvector |
| Redis | Docker Compose 또는 [Upstash](https://upstash.com) (Celery용, 선택) |

---

## 1. Supabase PostgreSQL 설정

1. [supabase.com](https://supabase.com) → **New Project** 생성
2. **Project Settings** → **Database** → Connection string (**URI**) 복사
3. **SQL Editor**에서 pgvector 활성화:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

4. Connection string 예시 (Pooler, 권장):

```
postgresql://postgres.[project-ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```

---

## 2. 로컬 개발 (Docker Compose)

```bash
cp backend/.env.example backend/.env
# .env에 YOUTUBE_API_KEY, OPENAI_API_KEY, Supabase DATABASE_URL 입력

docker compose up -d
```

- Frontend: `cd frontend && npm run dev` → http://localhost:5173
- Backend: http://localhost:8000/docs

로컬 DB를 쓰려면 `.env`에서 Supabase URL 대신 docker-compose 기본값 사용:

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/youtube_trends
```

---

## 3. Production Backend (Docker)

Supabase URL을 사용해 Backend만 Docker로 실행합니다.

```bash
cd backend
cp .env.example .env
# DATABASE_URL = Supabase connection string
# FRONTEND_URL = https://frontend-nu-five-48.vercel.app

docker build -t youtube-trend-backend .
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name youtube-trend-api \
  youtube-trend-backend
```

VPS(AWS EC2, DigitalOcean 등)에 올릴 때도 동일합니다.

---

## 4. Render로 Backend 호스팅 (선택, 무료)

1. [render.com](https://render.com) → GitHub 연동
2. **New Web Service** → `sharif9711/goorm_7` 선택
3. 설정:

| 항목 | 값 |
|------|-----|
| Root Directory | `backend` |
| Runtime | **Docker** |
| Health Check Path | `/health` |

4. **Environment Variables** 추가:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Supabase connection string |
| `YOUTUBE_API_KEY` | YouTube API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `SECRET_KEY` | 랜덤 32자+ 문자열 |
| `FRONTEND_URL` | `https://frontend-nu-five-48.vercel.app` |
| `PORT` | `8000` |

5. 배포 후 Render URL 예: `https://goorm-7-backend.onrender.com`

---

## 5. Vercel Frontend 연결

[Vercel Environment Variables](https://vercel.com/sharif9711s-projects/frontend/settings/environment-variables):

```
VITE_API_URL=https://your-backend-url/api
```

예 (Render): `https://goorm-7-backend.onrender.com/api`  
예 (VPS): `https://api.yourdomain.com/api`

저장 후 **Redeploy**.

---

## 6. Redis (선택 — Celery 주간 리포트)

**로컬:** `docker compose up redis` (이미 포함)

**Production — Upstash (무료):**

1. [upstash.com](https://upstash.com) → Redis 생성
2. Backend env에 설정:

```
REDIS_URL=rediss://...
CELERY_BROKER_URL=rediss://...
CELERY_RESULT_BACKEND=rediss://...
```

Celery worker 별도 실행:

```bash
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info
```

---

## Health Check

```bash
curl https://your-backend-url/health
# {"status":"ok","version":"1.0.0"}
```

## Troubleshooting

| 문제 | 해결 |
|------|------|
| DB 연결 실패 | Supabase URI에 `[password]`를 실제 비밀번호로 교체 |
| CORS 오류 | `FRONTEND_URL` = Vercel URL 확인 |
| pgvector 오류 | Supabase SQL Editor에서 `CREATE EXTENSION vector` 실행 |
| Frontend API 실패 | Vercel `VITE_API_URL` 끝에 `/api` 포함 확인 |
