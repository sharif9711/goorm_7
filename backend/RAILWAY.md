# Railway Backend Deployment

## Prerequisites

- [Railway account](https://railway.app)
- Railway CLI: `npm install -g @railway/cli`
- API keys: `YOUTUBE_API_KEY`, `OPENAI_API_KEY`

## Quick Deploy

```bash
cd backend
railway login
railway init --name goorm-7-backend
```

### 1. Add PostgreSQL

Railway Dashboard → **New** → **Database** → **PostgreSQL**

Railway automatically sets `DATABASE_URL` for the backend service.

> **pgvector**: For RAG embeddings, enable pgvector on PostgreSQL or use Supabase. The app runs without it (RAG disabled).

### 2. Add Redis (optional, for Celery)

**New** → **Database** → **Redis**

Set `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` from Redis connection string.

### 3. Set Environment Variables

| Variable | Value |
|----------|-------|
| `YOUTUBE_API_KEY` | Your YouTube Data API key |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SECRET_KEY` | Random 32+ char string |
| `FRONTEND_URL` | `https://frontend-nu-five-48.vercel.app` |
| `CORS_ORIGINS` | `["https://frontend-nu-five-48.vercel.app"]` |

```bash
railway variables set YOUTUBE_API_KEY=xxx OPENAI_API_KEY=xxx SECRET_KEY=xxx FRONTEND_URL=https://frontend-nu-five-48.vercel.app
```

### 4. Deploy

```bash
cd backend
railway up
```

Or connect GitHub repo: Railway Dashboard → **Deploy from GitHub** → select `sharif9711/goorm_7` → set **Root Directory** to `backend`.

### 5. Generate Public Domain

```bash
railway domain
```

### 6. Update Vercel Frontend

Set Vercel environment variable:

```
VITE_API_URL=https://your-railway-domain.up.railway.app/api
```

Redeploy Vercel after setting the variable.

## Health Check

```bash
curl https://your-railway-domain.up.railway.app/health
```

Expected: `{"status":"ok","version":"1.0.0"}`
