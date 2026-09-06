from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import UserRole
from app.db.session import get_db
from app.models.user import User
from app.models.vargani import Vargani
from app.schemas.common import VarganiOut, VarganiUpdate

router = APIRouter(prefix="/vargani", tags=["vargani"])


def to_out(row: Vargani) -> VarganiOut:
    return VarganiOut(
        id=row.id,
        member_id=row.member_id,
        member_name=row.member.name,
        house_number=row.member.house_number,
        phone=row.member.phone,
        expected_amount=row.expected_amount,
        amount_paid=row.amount_paid,
        pending_amount=row.pending_amount,
        status=row.status,
        payment_method=row.payment_method,
        payment_date=row.payment_date,
        receipt_number=row.receipt_number,
        screenshot_url=row.screenshot_url,
    )


@router.get("", response_model=list[VarganiOut])
def list_vargani(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Vargani).join(User)
    if current.role == UserRole.MEMBER:
        query = query.filter(Vargani.member_id == current.id)
    return [to_out(row) for row in query.all()]


@router.patch("/{vargani_id}", response_model=VarganiOut)
def update_vargani(
    vargani_id: int,
    payload: VarganiUpdate,
    _: User = Depends(require_roles(UserRole.TREASURER)),
    db: Session = Depends(get_db),
):
    row = db.query(Vargani).filter(Vargani.id == vargani_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Vargani record not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return to_out(row)


@router.get("/{vargani_id}/reminder")
def reminder_link(
    vargani_id: int,
    _: User = Depends(require_roles(UserRole.TREASURER)),
    db: Session = Depends(get_db),
):
    row = db.query(Vargani).filter(Vargani.id == vargani_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Vargani record not found")
    pending = int(row.pending_amount)
    message = (
        f"नमस्कार 🙏\nमंडळाची वर्गणी ₹{pending} बाकी आहे. "
        "कृपया शक्य तितक्या लवकर वर्गणी जमा करावी. धन्यवाद 🙏"
    )
    phone = row.member.phone
    url = f"https://wa.me/91{phone}?text={quote(message)}"
    return {"whatsapp_url": url, "message": message, "phone": phone}
