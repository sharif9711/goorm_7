#!/usr/bin/env python3
"""Supabase DB 연결 테스트 — backend/.env 필요"""
from __future__ import annotations

import asyncio
import ssl
import sys

import certifi


async def main() -> int:
    from urllib.parse import urlparse, unquote

    from app.core.config import get_settings
    from app.core.database import engine
    from sqlalchemy import text

    settings = get_settings()
    url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    parsed = urlparse(url)

    print("Host:", parsed.hostname)
    print("User:", parsed.username)
    print("Password set:", bool(parsed.password))

    if parsed.password and parsed.password.startswith("["):
        print("\n❌ 비밀번호에 [ ] 대괄호가 포함되어 있습니다.")
        print("   [YOUR-PASSWORD]를 실제 Supabase DB 비밀번호로 교체하세요.")
        return 1

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("\n✅ Supabase 연결 성공!", result.scalar())

            tables = await conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' ORDER BY table_name"
                )
            )
            names = [row[0] for row in tables.fetchall()]
            if names:
                print("Tables:", ", ".join(names))
            else:
                print("⚠️  테이블 없음 — Supabase SQL Editor에서 schema.sql 실행 필요")
        return 0
    except Exception as e:
        err = str(e)
        print(f"\n❌ 연결 실패: {type(e).__name__}")
        if "password authentication failed" in err.lower() or "InvalidPasswordError" in type(e).__name__:
            print("\n→ Supabase Database Password가 틀렸습니다.")
            print("  1. Supabase → Project Settings → Database")
            print("  2. Reset database password")
            print("  3. backend/.env 의 [YOUR-PASSWORD] 를 새 비밀번호로 교체")
            print("  (특수문자 @ # % 등은 URL 인코딩 필요 — setup-env.sh 사용 권장)")
        elif "certificate verify failed" in err.lower():
            print("\n→ SSL 인증서 문제. DEBUG=true 로 .env 설정 후 재시도")
        else:
            print(err[:200])
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
