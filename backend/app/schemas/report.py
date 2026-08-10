from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel


class CategoryBreakdownItem(BaseModel):
    major_category_id: int
    major_category_name: str
    amount: Decimal


class CategoryBreakdownRead(BaseModel):
    year: int
    month: int
    items: list[CategoryBreakdownItem]
    total: Decimal


class AssetTrendPoint(BaseModel):
    date: date_type
    total_balance: Decimal


class AssetTrendRead(BaseModel):
    items: list[AssetTrendPoint]
