from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import EventStatus, UserRole
from app.db.session import get_db
from app.models.event import FestivalEvent
from app.models.user import User
from app.schemas.common import EventCreate, EventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventOut])
def list_events(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(FestivalEvent).order_by(FestivalEvent.event_date).all()


@router.post("", response_model=EventOut)
def create_event(
    payload: EventCreate,
    current: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    event_time = None
    if payload.event_time:
        event_time = datetime.strptime(payload.event_time, "%H:%M").time()
    event = FestivalEvent(
        title=payload.title,
        event_date=payload.event_date,
        event_time=event_time,
        location=payload.location,
        responsible_person=payload.responsible_person,
        volunteers=payload.volunteers,
        budget=payload.budget,
        status=EventStatus(payload.status),
        created_by_id=current.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
