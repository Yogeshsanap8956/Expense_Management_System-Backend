from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PaymentMethod
from app.db.session import Base


class Vargani(Base):
    __tablename__ = "vargani"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    expected_amount: Mapped[float] = mapped_column(Float, default=1500)
    amount_paid: Mapped[float] = mapped_column(Float, default=0)
    payment_method: Mapped[PaymentMethod | None] = mapped_column(Enum(PaymentMethod), nullable=True)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    receipt_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    screenshot_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    member = relationship("User", back_populates="vargani")

    @property
    def pending_amount(self) -> float:
        return max(self.expected_amount - self.amount_paid, 0)

    @property
    def status(self) -> str:
        if self.amount_paid <= 0:
            return "pending"
        if self.amount_paid >= self.expected_amount:
            return "paid"
        return "partial"
