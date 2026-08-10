from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date_type
    amount: Decimal
    entry_kind: str
    entry_type: str
    major_category_id: int | None
    expense_category_id: int | None
    income_category_id: int | None
    asset_id: int
    memo: str | None


class TransactionListRead(BaseModel):
    items: list[TransactionRead]


class _TransactionFields(BaseModel):
    date: date_type
    amount: Decimal = Field(gt=0)
    entry_kind: str
    major_category_id: int | None = None
    expense_category_id: int | None = None
    income_category_id: int | None = None
    asset_id: int
    memo: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_category_consistency(self) -> "_TransactionFields":
        if self.entry_kind not in ("income", "expense"):
            raise ValueError("entry_kindはincomeまたはexpenseである必要があります")

        if self.entry_kind == "expense":
            if self.expense_category_id is None:
                raise ValueError("支出時はexpense_category_idが必須です")
            if self.income_category_id is not None:
                raise ValueError("支出時はincome_category_idを指定できません")
        else:
            if self.income_category_id is None:
                raise ValueError("収入時はincome_category_idが必須です")
            if self.expense_category_id is not None or self.major_category_id is not None:
                raise ValueError("収入時はmajor_category_id・expense_category_idを指定できません")
        return self


class TransactionCreate(_TransactionFields):
    pass


class TransactionUpdate(_TransactionFields):
    pass


class MonthlySummary(BaseModel):
    year: int
    month: int
    income_total: Decimal
    expense_total: Decimal
    balance: Decimal
