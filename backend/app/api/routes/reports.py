from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import report as report_crud
from app.db.session import get_db
from app.schemas.report import AssetTrendRead, CategoryBreakdownRead

ALLOWED_TREND_PERIODS = ("3m", "6m", "1y", "all")

router = APIRouter()


@router.get("/reports/category-breakdown", response_model=CategoryBreakdownRead)
def get_category_breakdown(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
) -> CategoryBreakdownRead:
    items = report_crud.get_category_breakdown(db, year, month)
    total = sum((item["amount"] for item in items), start=0)
    return CategoryBreakdownRead(year=year, month=month, items=items, total=total)


@router.get("/reports/asset-trend", response_model=AssetTrendRead)
def get_asset_trend(
    period: str = Query(...),
    db: Session = Depends(get_db),
) -> AssetTrendRead:
    if period not in ALLOWED_TREND_PERIODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="periodは3m・6m・1y・allのいずれかを指定してください",
        )
    items = report_crud.get_asset_trend(db, period)
    return AssetTrendRead(items=items)
