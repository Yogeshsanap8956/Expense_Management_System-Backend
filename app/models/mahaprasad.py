from datetime import date, datetime, time, timezone

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Mahaprasad(Base):
    __tablename__ = "mahaprasad"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prasad_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    menu: Mapped[str] = mapped_column(Text)
    expected_people: Mapped[int] = mapped_column(Integer, default=0)
    food_quantity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cooking_team: Mapped[str | None] = mapped_column(String(500), nullable=True)
    serving_team: Mapped[str | None] = mapped_column(String(500), nullable=True)
    volunteers: Mapped[str | None] = mapped_column(String(500), nullable=True)
    vendor: Mapped[str | None] = mapped_column(String(160), nullable=True)
    food_budget: Mapped[float] = mapped_column(Float, default=0)
    actual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    distribution_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
