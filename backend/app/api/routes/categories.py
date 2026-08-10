from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import category as category_crud
from app.db.session import get_db
from app.schemas.category import (
    ExpenseCategoryCreate,
    ExpenseCategoryRead,
    IncomeCategoryCreate,
    IncomeCategoryRead,
    MajorCategoryRead,
)

router = APIRouter()


@router.get("/major-categories", response_model=list[MajorCategoryRead])
def list_major_categories(db: Session = Depends(get_db)) -> list[MajorCategoryRead]:
    return category_crud.get_major_categories(db)


@router.get("/expense-categories", response_model=list[ExpenseCategoryRead])
def list_expense_categories(db: Session = Depends(get_db)) -> list[ExpenseCategoryRead]:
    return category_crud.get_expense_categories(db)


@router.post(
    "/expense-categories",
    response_model=ExpenseCategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_expense_category(
    payload: ExpenseCategoryCreate, db: Session = Depends(get_db)
) -> ExpenseCategoryRead:
    try:
        return category_crud.create_expense_category(
            db, major_category_id=payload.major_category_id, name=payload.name
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定された大カテゴリが存在しないか、同名の支出中カテゴリが既に存在します",
        ) from exc


@router.delete("/expense-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense_category(category_id: int, db: Session = Depends(get_db)) -> None:
    category = category_crud.get_expense_category(db, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="支出中カテゴリが見つかりません"
        )
    category_crud.delete_expense_category(db, category)


@router.get("/income-categories", response_model=list[IncomeCategoryRead])
def list_income_categories(db: Session = Depends(get_db)) -> list[IncomeCategoryRead]:
    return category_crud.get_income_categories(db)


@router.post(
    "/income-categories",
    response_model=IncomeCategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_income_category(
    payload: IncomeCategoryCreate, db: Session = Depends(get_db)
) -> IncomeCategoryRead:
    try:
        return category_crud.create_income_category(db, name=payload.name)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="同名の収入カテゴリが既に存在します",
        ) from exc


@router.delete("/income-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income_category(category_id: int, db: Session = Depends(get_db)) -> None:
    category = category_crud.get_income_category(db, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="収入カテゴリが見つかりません"
        )
    category_crud.delete_income_category(db, category)
