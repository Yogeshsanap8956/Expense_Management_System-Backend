from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.enums import ExpenseCategory, UserRole
from app.db.session import get_db
from app.models.expense import Expense
from app.models.user import User
from app.schemas.common import ExpenseCreate, ExpenseOut

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseOut])
def list_expenses(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Expense).order_by(Expense.expense_date.desc()).all()


@router.post("", response_model=ExpenseOut)
def create_expense(
    payload: ExpenseCreate,
    current: User = Depends(require_roles(UserRole.TREASURER)),
    db: Session = Depends(get_db),
):
    try:
        category = ExpenseCategory(payload.category)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid category") from exc
    expense = Expense(
        category=category,
        description=payload.description,
        amount=payload.amount,
        paid_to=payload.paid_to,
        expense_date=payload.expense_date,
        payment_method=payload.payment_method,
        bill_url=payload.bill_url,
        payment_screenshot_url=payload.payment_screenshot_url,
        notes=payload.notes,
        paid_by_id=current.id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/report")
def expense_report(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(Expense.category, func.coalesce(func.sum(Expense.amount), 0))
        .group_by(Expense.category)
        .all()
    )
    breakdown = [{"category": category.value if hasattr(category, "value") else str(category), "total": float(total)} for category, total in rows]
    grand_total = sum(item["total"] for item in breakdown)
    return {"breakdown": breakdown, "total": grand_total}


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    _: User = Depends(require_roles(UserRole.TREASURER)),
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"ok": True}
