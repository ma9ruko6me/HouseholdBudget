from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RecurringTransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    amount: Decimal
    entry_kind: str
    major_category_id: int | None
    expense_category_id: int | None
    income_category_id: int | None
    asset_id: int
    day_of_month: int
    last_generated_date: date_type | None
    memo: str | None


class RecurringTransactionListRead(BaseModel):
    items: list[RecurringTransactionRead]


class _RecurringTransactionFields(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    amount: Decimal = Field(gt=0)
    entry_kind: str
    major_category_id: int | None = None
    expense_category_id: int | None = None
    income_category_id: int | None = None
    asset_id: int
    day_of_month: int = Field(ge=1, le=31)
    memo: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_category_consistency(self) -> "_RecurringTransactionFields":
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


class RecurringTransactionCreate(_RecurringTransactionFields):
    pass


class RecurringTransactionUpdate(_RecurringTransactionFields):
    pass
