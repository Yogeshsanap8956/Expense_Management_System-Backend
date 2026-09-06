from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.models.vargani import Vargani
from app.schemas.common import LoginRequest, Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
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


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == payload.phone).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect phone or password")
    token = create_access_token(user.phone, user.role.value)
    return Token(access_token=token)


@router.post("/token", response_model=Token)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect phone or password")
    return Token(access_token=create_access_token(user.phone, user.role.value))


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current
