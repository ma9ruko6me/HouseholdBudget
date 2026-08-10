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
    transfer_to_asset_id: int | None
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
    transfer_to_asset_id: int | None = None
    memo: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_category_consistency(self) -> "_TransactionFields":
        if self.entry_kind not in ("income", "expense", "transfer"):
            raise ValueError("entry_kindはincome・expense・transferのいずれかである必要があります")

        if self.entry_kind == "expense":
            if self.expense_category_id is None:
                raise ValueError("支出時はexpense_category_idが必須です")
            if self.income_category_id is not None:
                raise ValueError("支出時はincome_category_idを指定できません")
            if self.transfer_to_asset_id is not None:
                raise ValueError("支出時はtransfer_to_asset_idを指定できません")
        elif self.entry_kind == "income":
            if self.income_category_id is None:
                raise ValueError("収入時はincome_category_idが必須です")
            if self.expense_category_id is not None or self.major_category_id is not None:
                raise ValueError("収入時はmajor_category_id・expense_category_idを指定できません")
            if self.transfer_to_asset_id is not None:
                raise ValueError("収入時はtransfer_to_asset_idを指定できません")
        else:
            if (
                self.major_category_id is not None
                or self.expense_category_id is not None
                or self.income_category_id is not None
            ):
                raise ValueError("振替時はカテゴリを指定できません")
            if self.transfer_to_asset_id is None:
                raise ValueError("振替時はtransfer_to_asset_idが必須です")
            if self.transfer_to_asset_id == self.asset_id:
                raise ValueError("移動元と移動先に同じ資産は指定できません")
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
