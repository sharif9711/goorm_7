# Supabase 설정 가이드 (단계별)

## Step 1 — 프로젝트 생성 (2분)

1. [https://supabase.com/dashboard](https://supabase.com/dashboard) 접속
2. **New Project** 클릭
3. 입력:
   - **Name**: `goorm-7` (아무 이름)
   - **Database Password**: 강력한 비밀번호 (메모 필수!)
   - **Region**: `Northeast Asia (Seoul)` 권장
4. **Create new project** → 1~2분 대기

---

## Step 2 — 스키마 생성 (1분)

1. 왼쪽 메뉴 **SQL Editor** 클릭
2. **New query** 클릭
3. [`backend/supabase/schema.sql`](../supabase/schema.sql) 파일 내용 전체 복사 → 붙여넣기
4. **Run** (또는 Cmd+Enter)
5. `Success. No rows returned` 확인

---

## Step 3 — Connection String 복사 (1분)

1. **Project Settings** (⚙️) → **Database**
2. **Connection string** 탭 → **URI** 선택
3. **Transaction pooler** (포트 `6543`) 권장
4. `[YOUR-PASSWORD]`를 Step 1에서 설정한 비밀번호로 교체
5. 복사된 URL 예시:

```
postgresql://postgres.abcdefgh:YOUR_PASSWORD@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```

---

## Step 4 — .env 설정 (1분)

터미널에서:

```bash
chmod +x scripts/setup-env.sh
./scripts/setup-env.sh
```

또는 `backend/.env`에 직접 입력:

```env
DATABASE_URL=postgresql+asyncpg://postgres.xxxx:PASSWORD@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
DATABASE_URL_SYNC=postgresql://postgres.xxxx:PASSWORD@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
YOUTUBE_API_KEY=your_key
OPENAI_API_KEY=your_key
SECRET_KEY=your_random_secret
FRONTEND_URL=https://frontend-nu-five-48.vercel.app
```

> `DATABASE_URL`은 `postgresql+asyncpg://` 로 시작해야 합니다 (`postgresql://` 앞에 `+asyncpg` 추가).

---

## Step 5 — Backend 실행

### Docker (권장)

```bash
docker compose -f docker-compose.prod.yml up -d
curl http://localhost:8000/health
```

### Python 직접 실행

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

정상 응답:
```json
{"status":"ok","version":"1.0.0"}
```

---

## Step 6 — Vercel 연결

1. [Vercel Environment Variables](https://vercel.com/sharif9711s-projects/frontend/settings/environment-variables)
2. 추가:

```
VITE_API_URL=http://localhost:8000/api   ← 로컬 테스트
VITE_API_URL=https://your-backend-url/api  ← Production
```

3. **Redeploy**

---

## 연결 테스트

```bash
# Backend health
curl http://localhost:8000/health

# 회원가입 테스트
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test","password":"password123"}'
```

Supabase Dashboard → **Table Editor** → `users` 테이블에 데이터 생성 확인

---

## 문제 해결

| 오류 | 해결 |
|------|------|
| `password authentication failed` | Supabase DB 비밀번호 재확인, URL의 `[YOUR-PASSWORD]` 교체 |
| `extension "vector" does not exist` | schema.sql Step 2 재실행 |
| `relation "users" does not exist` | schema.sql 미실행 — Step 2 진행 |
| `SSL required` | Supabase URL에 `?sslmode=require` 추가 |
| CORS error | `FRONTEND_URL` Vercel URL과 일치 확인 |
