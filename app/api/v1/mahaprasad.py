from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import UserRole
from app.db.session import get_db
from app.models.mahaprasad import Mahaprasad
from app.models.user import User
from app.schemas.common import MahaprasadCreate, MahaprasadUpdate

router = APIRouter(prefix="/mahaprasad", tags=["mahaprasad"])


def parse_time(value: str | None):
    if not value:
        return None
    return datetime.strptime(value, "%H:%M").time()


def serialize(item: Mahaprasad) -> dict:
    return {
        "id": item.id,
        "prasad_date": item.prasad_date,
        "menu": item.menu,
        "expected_people": item.expected_people,
        "food_quantity": item.food_quantity,
        "cooking_team": item.cooking_team,
        "serving_team": item.serving_team,
        "volunteers": item.volunteers,
        "vendor": item.vendor,
        "food_budget": item.food_budget,
        "actual_cost": item.actual_cost,
        "distribution_time": item.distribution_time.strftime("%H:%M") if item.distribution_time else None,
    }


@router.get("")
def list_prasad(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [serialize(item) for item in db.query(Mahaprasad).order_by(Mahaprasad.prasad_date).all()]


@router.post("")
def create_prasad(
    payload: MahaprasadCreate,
    _: User = Depends(require_roles(UserRole.PRASAD_COORDINATOR)),
    db: Session = Depends(get_db),
):
    if db.query(Mahaprasad).filter(Mahaprasad.prasad_date == payload.prasad_date).first():
        raise HTTPException(status_code=400, detail="Mahaprasad already exists for that date")
    item = Mahaprasad(
        prasad_date=payload.prasad_date,
        menu=payload.menu,
        expected_people=payload.expected_people,
        food_quantity=payload.food_quantity,
        cooking_team=payload.cooking_team,
        serving_team=payload.serving_team,
        volunteers=payload.volunteers,
        vendor=payload.vendor,
        food_budget=payload.food_budget,
        actual_cost=payload.actual_cost,
        distribution_time=parse_time(payload.distribution_time),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize(item)


@router.patch("/{prasad_id}")
def update_prasad(
    prasad_id: int,
    payload: MahaprasadUpdate,
    _: User = Depends(require_roles(UserRole.PRASAD_COORDINATOR)),
    db: Session = Depends(get_db),
):
    item = db.query(Mahaprasad).filter(Mahaprasad.id == prasad_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Mahaprasad not found")
    data = payload.model_dump(exclude_unset=True)
    if "distribution_time" in data:
        data["distribution_time"] = parse_time(data["distribution_time"])
    for field, value in data.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return serialize(item)


@router.post("/{prasad_id}/volunteer")
def volunteer(
    prasad_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(Mahaprasad).filter(Mahaprasad.id == prasad_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Mahaprasad not found")
    names = [name.strip() for name in (item.volunteers or "").split(",") if name.strip()]
    if current.name not in names:
        names.append(current.name)
        item.volunteers = ", ".join(names)
        db.commit()
        db.refresh(item)
    return serialize(item)
