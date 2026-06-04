#!/bin/bash
# Supabase + Backend .env 설정 스크립트
# 사용법: ./scripts/setup-env.sh

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/backend/.env"
EXAMPLE="$ROOT/backend/.env.example"

echo "============================================"
echo "  YouTube Trend Agent — 환경 변수 설정"
echo "============================================"
echo ""

if [ ! -f "$ENV_FILE" ]; then
  cp "$EXAMPLE" "$ENV_FILE"
  echo "✓ backend/.env 파일 생성됨"
fi

echo ""
echo "── Supabase Database URL ──"
echo "Supabase Dashboard → Project Settings → Database"
echo "→ Connection string → URI (Transaction pooler, port 6543 권장)"
echo ""
read -rp "DATABASE_URL (postgresql://...): " DB_URL

if [ -n "$DB_URL" ]; then
  # asyncpg 형식으로 변환
  ASYNC_URL="${DB_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"
  ASYNC_URL="${ASYNC_URL/postgres:\/\//postgresql+asyncpg:\/\/}"
  SYNC_URL="${DB_URL/postgresql+asyncpg:\/\//postgresql:\/\/}"
  SYNC_URL="${SYNC_URL/postgres:\/\//postgresql:\/\/}"

  if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
    sed -i.bak "s|^DATABASE_URL=.*|DATABASE_URL=$ASYNC_URL|" "$ENV_FILE"
  else
    echo "DATABASE_URL=$ASYNC_URL" >> "$ENV_FILE"
  fi

  if grep -q "^DATABASE_URL_SYNC=" "$ENV_FILE"; then
    sed -i.bak "s|^DATABASE_URL_SYNC=.*|DATABASE_URL_SYNC=$SYNC_URL|" "$ENV_FILE"
  else
    echo "DATABASE_URL_SYNC=$SYNC_URL" >> "$ENV_FILE"
  fi
  rm -f "$ENV_FILE.bak"
  echo "✓ DATABASE_URL 설정 완료"
fi

echo ""
read -rp "YOUTUBE_API_KEY: " YT_KEY
read -rp "OPENAI_API_KEY: " OAI_KEY
read -rp "SECRET_KEY (Enter = 자동 생성): " SECRET

if [ -z "$SECRET" ]; then
  SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
  echo "  → 자동 생성: $SECRET"
fi

for VAR_VAL in "YOUTUBE_API_KEY:$YT_KEY" "OPENAI_API_KEY:$OAI_KEY" "SECRET_KEY:$SECRET"; do
  KEY="${VAR_VAL%%:*}"
  VAL="${VAR_VAL#*:}"
  if [ -n "$VAL" ]; then
    if grep -q "^${KEY}=" "$ENV_FILE"; then
      sed -i.bak "s|^${KEY}=.*|${KEY}=${VAL}|" "$ENV_FILE"
    else
      echo "${KEY}=${VAL}" >> "$ENV_FILE"
    fi
  fi
done
rm -f "$ENV_FILE.bak"

# FRONTEND_URL 기본값
if ! grep -q "^FRONTEND_URL=" "$ENV_FILE"; then
  echo "FRONTEND_URL=https://frontend-nu-five-48.vercel.app" >> "$ENV_FILE"
fi

echo ""
echo "============================================"
echo "  설정 완료! backend/.env"
echo "============================================"
echo ""
echo "다음 단계:"
echo ""
echo "  1. Supabase SQL Editor에서 schema.sql 실행:"
echo "     backend/supabase/schema.sql"
echo ""
echo "  2. Backend 실행 (Docker):"
echo "     docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "  3. 또는 Python으로 직접 실행:"
echo "     cd backend && pip install -r requirements.txt"
echo "     alembic upgrade head  # schema.sql 실행했다면 생략 가능"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  4. Vercel에 VITE_API_URL 설정 후 Redeploy"
echo ""
