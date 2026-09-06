from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.enums import AartiSession
from app.db.session import get_db
from app.models.aarti import AartiAssignment, AartiSlot
from app.models.announcement import Announcement
from app.models.event import FestivalEvent
from app.models.expense import Expense
from app.models.mahaprasad import Mahaprasad
from app.models.user import User
from app.models.vargani import Vargani
from app.api.v1.events import serialize_event
from app.schemas.common import AnnouncementOut, DashboardOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def dashboard(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    collected = db.query(func.coalesce(func.sum(Vargani.amount_paid), 0)).scalar() or 0
    expected = db.query(func.coalesce(func.sum(Vargani.expected_amount), 0)).scalar() or 0
    spent = db.query(func.coalesce(func.sum(Expense.amount), 0)).scalar() or 0
    today = date.today()

    morning = (
        db.query(AartiSlot)
        .filter(AartiSlot.slot_date == today, AartiSlot.session == AartiSession.MORNING)
        .first()
    )
    evening = (
        db.query(AartiSlot)
        .filter(AartiSlot.slot_date == today, AartiSlot.session == AartiSession.EVENING)
        .first()
    )
    prasad = db.query(Mahaprasad).filter(Mahaprasad.prasad_date == today).first()
    aarti_count = 0
    if morning or evening:
        slot_ids = [slot.id for slot in [morning, evening] if slot]
        aarti_count = db.query(AartiAssignment).filter(AartiAssignment.slot_id.in_(slot_ids)).count()

    events = (
        db.query(FestivalEvent)
        .filter(FestivalEvent.event_date >= today)
        .order_by(FestivalEvent.event_date)
        .limit(6)
        .all()
    )
    announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).limit(5).all()

    return DashboardOut(
        mandal_name=settings.app_name,
        vargani_collected=float(collected),
        vargani_pending=float(max(expected - collected, 0)),
        vargani_expected=float(expected),
        expenses_spent=float(spent),
        balance=float(collected - spent),
        today_morning_aarti=morning.start_time.strftime("%I:%M %p") if morning else None,
        today_evening_aarti=evening.start_time.strftime("%I:%M %p") if evening else None,
        today_mahaprasad=prasad.distribution_time.strftime("%I:%M %p") if prasad and prasad.distribution_time else None,
        today_aarti_members=aarti_count,
        upcoming_events=[serialize_event(event) for event in events],
        announcements=[AnnouncementOut.model_validate(item) for item in announcements],
    )
