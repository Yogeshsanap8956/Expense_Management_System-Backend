from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import AartiSession, UserRole
from app.db.session import get_db
from app.models.aarti import AartiAssignment, AartiAvailability, AartiSlot
from app.models.user import User
from app.schemas.common import AartiAssignRequest, AartiDayCreate, AartiSlotCreate, AvailabilityUpdate

router = APIRouter(prefix="/aarti", tags=["aarti"])


def serialize_slot(slot: AartiSlot, db: Session, current: User) -> dict:
    assigned = (
        db.query(User)
        .join(AartiAssignment, AartiAssignment.member_id == User.id)
        .filter(AartiAssignment.slot_id == slot.id)
        .all()
    )
    availability_rows = (
        db.query(AartiAvailability, User)
        .join(User, User.id == AartiAvailability.member_id)
        .filter(AartiAvailability.slot_id == slot.id)
        .all()
    )
    mine = next((row.available for row, _ in availability_rows if row.member_id == current.id), None)
    return {
        "id": slot.id,
        "slot_date": slot.slot_date,
        "session": slot.session.value,
        "start_time": slot.start_time.strftime("%H:%M"),
        "notes": slot.notes,
        "members": [{"id": member.id, "name": member.name} for member in assigned],
        "availability": [
            {"member_id": user.id, "name": user.name, "available": row.available}
            for row, user in availability_rows
        ],
        "my_availability": mine,
    }


@router.get("")
def list_slots(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    slots = db.query(AartiSlot).order_by(AartiSlot.slot_date, AartiSlot.session).all()
    return [serialize_slot(slot, db, current) for slot in slots]


@router.post("")
def create_slot(
    payload: AartiSlotCreate,
    _: User = Depends(require_roles(UserRole.AARTI_COORDINATOR)),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(AartiSlot)
        .filter(AartiSlot.slot_date == payload.slot_date, AartiSlot.session == AartiSession(payload.session))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Aarti slot already exists for that date and session")
    slot = AartiSlot(
        slot_date=payload.slot_date,
        session=AartiSession(payload.session),
        start_time=datetime.strptime(payload.start_time, "%H:%M").time(),
        notes=payload.notes,
    )
    db.add(slot)
    db.flush()
    for member_id in dict.fromkeys(payload.member_ids):
        db.add(AartiAssignment(slot_id=slot.id, member_id=member_id))
    db.commit()
    db.refresh(slot)
    return {"id": slot.id}


@router.post("/days")
def create_day(
    payload: AartiDayCreate,
    current: User = Depends(require_roles(UserRole.AARTI_COORDINATOR)),
    db: Session = Depends(get_db),
):
    created = []
    for session, start in (
        (AartiSession.MORNING, payload.morning_time),
        (AartiSession.EVENING, payload.evening_time),
    ):
        exists = (
            db.query(AartiSlot)
            .filter(AartiSlot.slot_date == payload.slot_date, AartiSlot.session == session)
            .first()
        )
        if exists:
            continue
        slot = AartiSlot(
            slot_date=payload.slot_date,
            session=session,
            start_time=datetime.strptime(start, "%H:%M").time(),
        )
        db.add(slot)
        db.flush()
        created.append(slot.id)
    db.commit()
    slots = db.query(AartiSlot).filter(AartiSlot.slot_date == payload.slot_date).all()
    return [serialize_slot(slot, db, current) for slot in slots]


@router.post("/availability")
def set_availability(
    payload: AvailabilityUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    slot = db.query(AartiSlot).filter(AartiSlot.id == payload.slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Aarti slot not found")
    row = (
        db.query(AartiAvailability)
        .filter(AartiAvailability.slot_id == payload.slot_id, AartiAvailability.member_id == current.id)
        .first()
    )
    if row:
        row.available = payload.available
    else:
        db.add(AartiAvailability(slot_id=payload.slot_id, member_id=current.id, available=payload.available))
    db.commit()
    db.refresh(slot)
    return serialize_slot(slot, db, current)


@router.post("/{slot_id}/assign")
def assign_members(
    slot_id: int,
    payload: AartiAssignRequest,
    current: User = Depends(require_roles(UserRole.AARTI_COORDINATOR)),
    db: Session = Depends(get_db),
):
    slot = db.query(AartiSlot).filter(AartiSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Aarti slot not found")
    db.query(AartiAssignment).filter(AartiAssignment.slot_id == slot_id).delete()
    for member_id in dict.fromkeys(payload.member_ids):
        member = db.query(User).filter(User.id == member_id, User.is_active.is_(True)).first()
        if not member:
            raise HTTPException(status_code=400, detail=f"Member {member_id} not found")
        db.add(AartiAssignment(slot_id=slot_id, member_id=member_id))
    db.commit()
    db.refresh(slot)
    return serialize_slot(slot, db, current)
