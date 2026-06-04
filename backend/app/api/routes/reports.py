from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.report import Report
from app.models.user import User
from app.schemas.analysis import ReportCreate, ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportResponse])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
):
    result = await db.execute(
        select(Report).where(Report.user_id == user.id).order_by(desc(Report.created_at)).limit(limit)
    )
    return result.scalars().all()


@router.post("", response_model=ReportResponse)
async def create_report(
    data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = Report(
        user_id=user.id,
        project_id=data.project_id,
        title=data.title,
        summary=data.summary,
        markdown_content=data.markdown_content,
        analysis_type=data.analysis_type,
    )
    db.add(report)
    await db.flush()
    return report


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/pdf")
async def download_report_pdf(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        import markdown
        from weasyprint import HTML

        html_content = markdown.markdown(report.markdown_content or "")
        pdf = HTML(string=f"<html><body>{html_content}</body></html>").write_pdf()
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="report-{report_id}.pdf"'},
        )
    except Exception:
        raise HTTPException(status_code=500, detail="PDF generation failed")
