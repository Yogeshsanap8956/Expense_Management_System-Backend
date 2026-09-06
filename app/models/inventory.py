from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import InventoryStatus
from app.db.session import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    total_quantity: Mapped[int] = mapped_column(Integer, default=0)
    used_quantity: Mapped[int] = mapped_column(Integer, default=0)
    returned_quantity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[InventoryStatus] = mapped_column(Enum(InventoryStatus), default=InventoryStatus.AVAILABLE)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def available_quantity(self) -> int:
        return max(self.total_quantity - self.used_quantity + self.returned_quantity, 0)
