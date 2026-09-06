from datetime import date, datetime, time, timezone

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AartiSession
from app.db.session import Base


class AartiSlot(Base):
    __tablename__ = "aarti_slots"
    __table_args__ = (UniqueConstraint("slot_date", "session", name="uq_aarti_date_session"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_date: Mapped[date] = mapped_column(Date, index=True)
    session: Mapped[AartiSession] = mapped_column(Enum(AartiSession))
    start_time: Mapped[time] = mapped_column(Time)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    assignments = relationship("AartiAssignment", back_populates="slot", cascade="all, delete-orphan")
    availability = relationship("AartiAvailability", back_populates="slot", cascade="all, delete-orphan")


class AartiAssignment(Base):
    __tablename__ = "aarti_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_id: Mapped[int] = mapped_column(ForeignKey("aarti_slots.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    slot = relationship("AartiSlot", back_populates="assignments")


class AartiAvailability(Base):
    __tablename__ = "aarti_availability"
    __table_args__ = (UniqueConstraint("slot_id", "member_id", name="uq_availability_slot_member"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_id: Mapped[int] = mapped_column(ForeignKey("aarti_slots.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    available: Mapped[bool] = mapped_column(Boolean, default=True)

    slot = relationship("AartiSlot", back_populates="availability")
