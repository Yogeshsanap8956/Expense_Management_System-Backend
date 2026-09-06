from io import BytesIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.expense import Expense
from app.models.user import User
from app.models.vargani import Vargani

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/final")
def final_report(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expected = db.query(func.coalesce(func.sum(Vargani.expected_amount), 0)).scalar() or 0
    collected = db.query(func.coalesce(func.sum(Vargani.amount_paid), 0)).scalar() or 0
    spent_rows = db.query(Expense.category, func.coalesce(func.sum(Expense.amount), 0)).group_by(Expense.category).all()
    expenses = [{"category": c.value if hasattr(c, "value") else str(c), "total": float(t)} for c, t in spent_rows]
    total_expenses = sum(item["total"] for item in expenses)
    return {
        "festival": "GANPATI FESTIVAL 2026",
        "mandal_name": settings.app_name,
        "vargani": {
            "expected": float(expected),
            "collected": float(collected),
            "pending": float(max(expected - collected, 0)),
        },
        "expenses": expenses,
        "total_expenses": total_expenses,
        "balance": float(collected - total_expenses),
    }


@router.get("/final.pdf")
def final_report_pdf(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data_resp = final_report(_, db)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 60
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, f"{data_resp['mandal_name']}")
    y -= 24
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, data_resp["festival"])
    y -= 36
    pdf.setFont("Helvetica", 12)
    v = data_resp["vargani"]
    pdf.drawString(50, y, f"Vargani expected: Rs {v['expected']}")
    y -= 18
    pdf.drawString(50, y, f"Collected: Rs {v['collected']}")
    y -= 18
    pdf.drawString(50, y, f"Pending: Rs {v['pending']}")
    y -= 30
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Expenses")
    y -= 20
    pdf.setFont("Helvetica", 11)
    for item in data_resp["expenses"]:
        pdf.drawString(60, y, f"{item['category']}: Rs {item['total']}")
        y -= 16
    y -= 10
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, f"Total expenses: Rs {data_resp['total_expenses']}")
    y -= 18
    pdf.drawString(50, y, f"Balance: Rs {data_resp['balance']}")
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=ganpati-final-report.pdf"},
    )
