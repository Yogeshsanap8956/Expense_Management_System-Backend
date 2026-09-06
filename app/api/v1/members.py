from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import UserRole
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User
from app.models.vargani import Vargani
from app.schemas.common import UserCreate, UserOut

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=list[UserOut])
def list_members(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.house_number, User.name).all()


@router.post("", response_model=UserOut)
def create_member(
    payload: UserCreate,
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.TREASURER)),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="Phone already exists")
    user = User(
        name=payload.name,
        phone=payload.phone,
        house_number=payload.house_number,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    db.add(Vargani(member_id=user.id, expected_amount=payload.expected_vargani))
    db.commit()
    db.refresh(user)
    return user
