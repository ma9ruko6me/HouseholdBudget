from decimal import Decimal

from sqlalchemy import DECIMAL, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

AssetType = Enum("bank", "cash", "credit_card", name="asset_type")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(AssetType, nullable=False)
    balance: Mapped[Decimal] = mapped_column(DECIMAL(12, 0), nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(nullable=False)
