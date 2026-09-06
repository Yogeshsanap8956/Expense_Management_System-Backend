from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import AartiSession, UserRole
from app.db.session import get_db
from app.models.aarti import AartiAssignment, AartiAvailability, AartiSlot
from app.models.user import User
from app.schemas.common import AartiSlotCreate, AvailabilityUpdate

router = APIRouter(prefix="/aarti", tags=["aarti"])


@router.get("")
def list_slots(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    slots = db.query(AartiSlot).order_by(AartiSlot.slot_date, AartiSlot.session).all()
    result = []
    for slot in slots:
        members = db.query(User).join(AartiAssignment, AartiAssignment.member_id == User.id).filter(AartiAssignment.slot_id == slot.id).all()
        result.append(
            {
                "id": slot.id,
                "slot_date": slot.slot_date,
                "session": slot.session.value,
                "start_time": slot.start_time.strftime("%H:%M"),
                "notes": slot.notes,
                "members": [{"id": m.id, "name": m.name} for m in members],
            }
        )
    return result


@router.post("")
def create_slot(
    payload: AartiSlotCreate,
    _: User = Depends(require_roles(UserRole.AARTI_COORDINATOR)),
    db: Session = Depends(get_db),
):
    slot = AartiSlot(
        slot_date=payload.slot_date,
        session=AartiSession(payload.session),
        start_time=datetime.strptime(payload.start_time, "%H:%M").time(),
        notes=payload.notes,
    )
    db.add(slot)
    db.flush()
    for member_id in payload.member_ids:
        db.add(AartiAssignment(slot_id=slot.id, member_id=member_id))
    db.commit()
    db.refresh(slot)
    return {"id": slot.id}


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
    return {"ok": True}
