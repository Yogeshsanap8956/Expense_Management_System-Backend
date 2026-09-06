from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ExpenseCategory, PaymentMethod
from app.db.session import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[ExpenseCategory] = mapped_column(Enum(ExpenseCategory))
    description: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Float)
    paid_to: Mapped[str] = mapped_column(String(120))
    expense_date: Mapped[date] = mapped_column(Date)
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod))
    bill_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_screenshot_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    paid_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    paid_by_user = relationship("User", back_populates="expenses")
