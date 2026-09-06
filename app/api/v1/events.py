from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import EventStatus, UserRole
from app.db.session import get_db
from app.models.event import FestivalEvent
from app.models.user import User
from app.schemas.common import EventCreate, EventOut, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


def parse_time(value: str | None):
    if not value:
        return None
    return datetime.strptime(value[:5], "%H:%M").time()


def serialize_event(event: FestivalEvent) -> dict:
    return {
        "id": event.id,
        "title": event.title,
        "event_date": event.event_date,
        "event_time": event.event_time.strftime("%H:%M") if event.event_time else None,
        "location": event.location,
        "responsible_person": event.responsible_person,
        "volunteers": event.volunteers,
        "budget": event.budget,
        "status": event.status.value if hasattr(event.status, "value") else event.status,
    }


@router.get("", response_model=list[EventOut])
def list_events(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [serialize_event(row) for row in db.query(FestivalEvent).order_by(FestivalEvent.event_date).all()]


@router.post("", response_model=EventOut)
def create_event(
    payload: EventCreate,
    current: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    event = FestivalEvent(
        title=payload.title,
        event_date=payload.event_date,
        event_time=parse_time(payload.event_time),
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
    return serialize_event(event)


@router.patch("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    event = db.query(FestivalEvent).filter(FestivalEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    data = payload.model_dump(exclude_unset=True)
    if "event_time" in data:
        event.event_time = parse_time(data.pop("event_time"))
    if "status" in data and data["status"] is not None:
        event.status = EventStatus(data.pop("status"))
    for field, value in data.items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return serialize_event(event)
