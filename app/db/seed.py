from datetime import date, time

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import AartiSession, ExpenseCategory, PaymentMethod, UserRole
from app.core.security import hash_password
from app.models.aarti import AartiAssignment, AartiSlot
from app.models.announcement import Announcement
from app.models.event import FestivalEvent
from app.models.expense import Expense
from app.models.inventory import InventoryItem
from app.models.mahaprasad import Mahaprasad
from app.models.user import User
from app.models.vargani import Vargani


def seed_if_empty(db: Session) -> None:
    if db.query(User).first():
        return

    admin = User(
        name=settings.admin_name,
        phone=settings.admin_phone,
        house_number="A-100",
        role=UserRole.ADMIN,
        hashed_password=hash_password(settings.admin_password),
    )
    db.add(admin)
    db.flush()

    members = [
        ("Amit", "9000000001", "A-101", UserRole.MEMBER, 1500, 1500),
        ("Rahul", "9000000002", "A-102", UserRole.MEMBER, 1500, 0),
        ("Sagar", "9000000003", "A-103", UserRole.MEMBER, 1500, 1500),
        ("Rohit", "9000000004", "A-104", UserRole.AARTI_COORDINATOR, 1500, 1500),
        ("Yogesh", "9000000005", "A-105", UserRole.TREASURER, 1500, 1500),
        ("Prasad", "9000000006", "A-106", UserRole.PRASAD_COORDINATOR, 1500, 0),
        ("Nilesh", "9000000007", "B-201", UserRole.MEMBER, 1500, 1500),
        ("Akshay", "9000000008", "B-202", UserRole.MEMBER, 1500, 0),
    ]
    created = []
    for name, phone, house, role, expected, paid in members:
        user = User(
            name=name,
            phone=phone,
            house_number=house,
            role=role,
            hashed_password=hash_password("member123"),
        )
        db.add(user)
        db.flush()
        db.add(
            Vargani(
                member_id=user.id,
                expected_amount=expected,
                amount_paid=paid,
                payment_method=PaymentMethod.UPI if paid else None,
                payment_date=date(2026, 9, 5) if paid else None,
                receipt_number=f"R-{house}" if paid else None,
            )
        )
        created.append(user)

    db.add(Vargani(member_id=admin.id, expected_amount=1500, amount_paid=1500, payment_method=PaymentMethod.CASH))

    db.add_all(
        [
            Expense(
                category=ExpenseCategory.DECORATION,
                description="Lights",
                amount=8500,
                paid_to="XYZ Electrical",
                expense_date=date(2026, 9, 5),
                payment_method=PaymentMethod.UPI,
                paid_by_id=admin.id,
            ),
            Expense(
                category=ExpenseCategory.SOUND_SYSTEM,
                description="Speakers and mic",
                amount=12000,
                paid_to="Audio House",
                expense_date=date(2026, 9, 5),
                payment_method=PaymentMethod.CASH,
                paid_by_id=admin.id,
            ),
            Expense(
                category=ExpenseCategory.PRASAD,
                description="Mahaprasad groceries",
                amount=8750,
                paid_to="Local Kirana",
                expense_date=date(2026, 9, 6),
                payment_method=PaymentMethod.UPI,
                paid_by_id=admin.id,
            ),
        ]
    )

    today = date(2026, 9, 6)
    morning = AartiSlot(slot_date=today, session=AartiSession.MORNING, start_time=time(6, 30))
    evening = AartiSlot(slot_date=today, session=AartiSession.EVENING, start_time=time(19, 30))
    db.add_all([morning, evening])
    db.flush()
    for user in created[:5]:
        db.add(AartiAssignment(slot_id=morning.id, member_id=user.id))
    for user in created[5:]:
        db.add(AartiAssignment(slot_id=evening.id, member_id=user.id))

    db.add(
        Mahaprasad(
            prasad_date=today,
            menu="Rice, Dal, Potato Bhaji, Salad, Shrikhand",
            expected_people=350,
            cooking_team="Ramesh, Suresh, Akshay, Prasad",
            food_budget=12000,
            distribution_time=time(13, 0),
        )
    )
    db.add(
        Announcement(
            title="IMPORTANT",
            body="Tomorrow's evening Aarti will be at 7:30 PM. All members are requested to be present 15 minutes before Aarti. गणपती बाप्पा मोरया 🙏",
            created_by_id=admin.id,
        )
    )
    db.add_all(
        [
            FestivalEvent(title="Ganpati Sthapana", event_date=date(2026, 9, 5), created_by_id=admin.id),
            FestivalEvent(title="Aarti + Mahaprasad", event_date=date(2026, 9, 6), created_by_id=admin.id),
            FestivalEvent(title="Cultural Program", event_date=date(2026, 9, 7), created_by_id=admin.id),
            FestivalEvent(title="Visarjan", event_date=date(2026, 9, 11), created_by_id=admin.id),
        ]
    )
    db.add_all(
        [
            InventoryItem(name="Plastic Chairs", total_quantity=120),
            InventoryItem(name="Tables", total_quantity=12),
            InventoryItem(name="Mic", total_quantity=4),
            InventoryItem(name="Speakers", total_quantity=2),
            InventoryItem(name="Extension Boards", total_quantity=8),
        ]
    )
    db.commit()


def ensure_festival_aarti_slots(db: Session) -> None:
    extras = [
        (date(2026, 9, 7), time(6, 30), time(19, 30)),
        (date(2026, 9, 8), time(6, 30), time(19, 30)),
    ]
    changed = False
    for slot_date, morning, evening in extras:
        if db.query(AartiSlot).filter(AartiSlot.slot_date == slot_date).first():
            continue
        db.add(AartiSlot(slot_date=slot_date, session=AartiSession.MORNING, start_time=morning))
        db.add(AartiSlot(slot_date=slot_date, session=AartiSession.EVENING, start_time=evening))
        changed = True
    if changed:
        db.commit()
