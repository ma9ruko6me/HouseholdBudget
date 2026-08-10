from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.transaction import TransactionRead


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    balance: Decimal
    sort_order: int


class AssetListRead(BaseModel):
    items: list[AssetRead]
    total_balance: Decimal


class AssetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    type: str
    balance: Decimal = Decimal(0)


class AssetUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    type: str


class AssetAdjust(BaseModel):
    actual_balance: Decimal


class AssetAdjustResult(BaseModel):
    asset: AssetRead
    transaction: TransactionRead | None
