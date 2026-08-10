from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import asset as asset_crud
from app.db.session import get_db
from app.models import Asset
from app.schemas.asset import (
    AssetAdjust,
    AssetAdjustResult,
    AssetCreate,
    AssetListRead,
    AssetRead,
    AssetUpdate,
)

router = APIRouter()

VALID_ASSET_TYPES = {"bank", "cash", "credit_card"}


def _validate_type(type_: str) -> None:
    if type_ not in VALID_ASSET_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"typeは{sorted(VALID_ASSET_TYPES)}のいずれかである必要があります",
        )


@router.get("/assets", response_model=AssetListRead)
def list_assets(db: Session = Depends(get_db)) -> AssetListRead:
    items = asset_crud.get_assets(db)
    total_balance = asset_crud.get_total_balance(db)
    return AssetListRead(items=items, total_balance=total_balance)


@router.post("/assets", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)) -> AssetRead:
    _validate_type(payload.type)
    try:
        return asset_crud.create_asset(
            db, name=payload.name, type_=payload.type, balance=payload.balance
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="資産の登録に失敗しました"
        ) from exc


def _get_asset_or_404(db: Session, asset_id: int) -> Asset:
    asset = asset_crud.get_asset(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="資産が見つかりません")
    return asset


@router.put("/assets/{asset_id}", response_model=AssetRead)
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)) -> AssetRead:
    _validate_type(payload.type)
    asset = _get_asset_or_404(db, asset_id)
    return asset_crud.update_asset(db, asset, name=payload.name, type_=payload.type)


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)) -> None:
    asset = _get_asset_or_404(db, asset_id)
    if asset_crud.is_asset_referenced(db, asset_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="取引または定期取引で使用中のため削除できません",
        )
    asset_crud.delete_asset(db, asset)


@router.post("/assets/{asset_id}/adjust", response_model=AssetAdjustResult)
def adjust_asset(
    asset_id: int, payload: AssetAdjust, db: Session = Depends(get_db)
) -> AssetAdjustResult:
    asset = _get_asset_or_404(db, asset_id)
    transaction = asset_crud.adjust_asset_balance(db, asset, payload.actual_balance)
    return AssetAdjustResult(asset=asset, transaction=transaction)
