from datetime import date, datetime, time, timezone

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EventStatus
from app.db.session import Base


class FestivalEvent(Base):
    __tablename__ = "festival_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    event_date: Mapped[date] = mapped_column(Date, index=True)
    event_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    location: Mapped[str | None] = mapped_column(String(160), nullable=True)
    responsible_person: Mapped[str | None] = mapped_column(String(120), nullable=True)
    volunteers: Mapped[str | None] = mapped_column(String(500), nullable=True)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), default=EventStatus.PLANNED)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
