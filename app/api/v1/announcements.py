from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import UserRole
from app.db.session import get_db
from app.models.announcement import Announcement
from app.models.user import User
from app.schemas.common import AnnouncementCreate, AnnouncementOut

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.get("", response_model=list[AnnouncementOut])
def list_announcements(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).all()


@router.post("", response_model=AnnouncementOut)
def create_announcement(
    payload: AnnouncementCreate,
    current: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    item = Announcement(**payload.model_dump(), created_by_id=current.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{announcement_id}/share")
def share_announcement(
    announcement_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Announcement not found")
    message = (
        f"📢 {item.title}\n\n{item.body}\n\n"
        "— श्री गणेश मित्र मंडळ 🙏"
    )
    return {"whatsapp_url": f"https://wa.me/?text={quote(message)}", "message": message}
