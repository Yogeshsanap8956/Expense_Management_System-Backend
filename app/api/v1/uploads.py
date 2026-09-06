from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import require_roles
from app.core.config import settings
from app.core.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic", "application/pdf"}
MAX_BYTES = 8 * 1024 * 1024


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    _: User = Depends(require_roles(UserRole.TREASURER)),
):
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, WEBP or PDF files are allowed")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="File must be 8 MB or smaller")
    suffix = Path(file.filename or "bill.jpg").suffix.lower() or ".jpg"
    if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".heic", ".pdf"}:
        suffix = ".jpg"
    folder = Path(settings.upload_dir)
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{suffix}"
    (folder / filename).write_bytes(data)
    return {"url": f"/uploads/{filename}", "filename": file.filename, "content_type": content_type}
