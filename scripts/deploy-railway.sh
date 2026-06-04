#!/bin/bash
# Railway Backend 배포 스크립트
# 사용법: ./scripts/deploy-railway.sh

set -e

cd "$(dirname "$0")/../backend"

echo "=== Railway Backend Deploy ==="

if ! command -v railway &>/dev/null; then
  echo "Installing Railway CLI..."
  npm install -g @railway/cli
fi

if ! railway whoami &>/dev/null; then
  echo "Railway 로그인이 필요합니다: railway login"
  railway login
fi

echo "프로젝트 연결/생성..."
railway link || railway init --name goorm-7-backend

echo "PostgreSQL 추가 (없는 경우 Railway Dashboard에서 Add Plugin > PostgreSQL)..."
echo "Redis 추가 (선택, Celery용)..."

echo "환경 변수 설정 (Dashboard 또는 CLI로 설정 필요):"
echo "  YOUTUBE_API_KEY, OPENAI_API_KEY, SECRET_KEY, FRONTEND_URL"

railway variables set FRONTEND_URL=https://frontend-nu-five-48.vercel.app || true

echo "배포 시작..."
railway up --detach

echo ""
echo "배포 완료! Backend URL 확인:"
railway domain || echo "railway domain 명령으로 URL 확인"
