from __future__ import annotations

from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.embedding import EmbeddingDocument
from app.services.openai_service import OpenAIService

settings = get_settings()


class RAGService:
    def __init__(self, openai: OpenAIService | None = None):
        self.openai = openai or OpenAIService()

    async def index_content(
        self,
        db: AsyncSession,
        source_type: str,
        source_id: str,
        content: str,
    ) -> None:
        if not content.strip():
            return

        chunks = self._chunk_text(content)
        for i, chunk in enumerate(chunks):
            embedding = await self.openai.create_embedding(chunk)
            doc = EmbeddingDocument(
                source_type=source_type,
                source_id=f"{source_id}_{i}",
                content=chunk,
                embedding=embedding,
            )
            db.add(doc)

    async def search(self, db: AsyncSession, query: str, limit: int = 5) -> list[dict[str, Any]]:
        query_embedding = await self.openai.create_embedding(query)
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        result = await db.execute(
            text(
                f"""
                SELECT id, source_type, source_id, content,
                       1 - (embedding <=> '{embedding_str}'::vector) AS similarity
                FROM embedding_documents
                ORDER BY embedding <=> '{embedding_str}'::vector
                LIMIT :limit
                """
            ),
            {"limit": limit},
        )
        rows = result.fetchall()
        return [
            {
                "id": row[0],
                "source_type": row[1],
                "source_id": row[2],
                "content": row[3],
                "similarity": float(row[4]) if row[4] else 0,
            }
            for row in rows
        ]

    async def answer_with_context(self, db: AsyncSession, query: str) -> str:
        docs = await self.search(db, query)
        if not docs:
            return "관련 데이터를 찾을 수 없습니다."

        context = "\n\n".join(d["content"] for d in docs)
        if not self.openai.client:
            return f"검색 결과:\n{context[:2000]}"

        response = await self.openai.client.chat.completions.create(
            model=self.openai.model,
            messages=[
                {"role": "system", "content": "YouTube 트렌드 데이터를 기반으로 한국어로 답변하세요."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
            ],
        )
        return response.choices[0].message.content or ""

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
        return chunks or [text]
