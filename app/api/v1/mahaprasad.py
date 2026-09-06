from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import UserRole
from app.db.session import get_db
from app.models.mahaprasad import Mahaprasad
from app.models.user import User
from app.schemas.common import MahaprasadCreate

router = APIRouter(prefix="/mahaprasad", tags=["mahaprasad"])


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
    dist = datetime.strptime(payload.distribution_time, "%H:%M").time() if payload.distribution_time else None
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
        distribution_time=dist,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize(item)
