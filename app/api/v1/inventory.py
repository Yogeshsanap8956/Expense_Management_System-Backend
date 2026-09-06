from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import InventoryStatus, UserRole
from app.db.session import get_db
from app.models.inventory import InventoryItem
from app.models.user import User
from app.schemas.common import InventoryCreate

router = APIRouter(prefix="/inventory", tags=["inventory"])


def serialize(item: InventoryItem) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "total_quantity": item.total_quantity,
        "used_quantity": item.used_quantity,
        "returned_quantity": item.returned_quantity,
        "available_quantity": item.available_quantity,
        "status": item.status.value,
        "notes": item.notes,
    }


@router.get("")
def list_inventory(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [serialize(item) for item in db.query(InventoryItem).order_by(InventoryItem.name).all()]


@router.post("")
def create_item(
    payload: InventoryCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    item = InventoryItem(**payload.model_dump(), status=InventoryStatus.AVAILABLE)
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize(item)
