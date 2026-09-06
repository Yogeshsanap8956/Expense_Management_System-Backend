from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import PaymentMethod, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    phone: str
    password: str


class UserCreate(BaseModel):
    name: str
    phone: str
    password: str = Field(min_length=4)
    house_number: Optional[str] = None
    role: UserRole = UserRole.MEMBER
    expected_vargani: float = 1500


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    house_number: Optional[str]
    role: UserRole
    is_active: bool


class VarganiUpdate(BaseModel):
    expected_amount: Optional[float] = None
    amount_paid: Optional[float] = None
    payment_method: Optional[PaymentMethod] = None
    payment_date: Optional[date] = None
    receipt_number: Optional[str] = None
    screenshot_url: Optional[str] = None


class VarganiOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int
    member_name: str
    house_number: Optional[str]
    phone: str
    expected_amount: float
    amount_paid: float
    pending_amount: float
    status: str
    payment_method: Optional[PaymentMethod]
    payment_date: Optional[date]
    receipt_number: Optional[str]
    screenshot_url: Optional[str]


class ExpenseCreate(BaseModel):
    category: str
    description: str
    amount: float
    paid_to: str
    expense_date: date
    payment_method: PaymentMethod
    bill_url: Optional[str] = None
    payment_screenshot_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseUpdate(BaseModel):
    bill_url: Optional[str] = None
    payment_screenshot_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    category: str
    description: str
    amount: float
    paid_to: str
    expense_date: date
    payment_method: PaymentMethod
    bill_url: Optional[str]
    payment_screenshot_url: Optional[str]
    notes: Optional[str]
    paid_by_id: int


class AnnouncementCreate(BaseModel):
    title: str
    body: str
    is_important: bool = True


class AnnouncementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    is_important: bool
    created_at: datetime


class EventCreate(BaseModel):
    title: str
    event_date: date
    event_time: Optional[str] = None
    location: Optional[str] = None
    responsible_person: Optional[str] = None
    volunteers: Optional[str] = None
    budget: Optional[float] = None
    status: str = "planned"


class EventUpdate(BaseModel):
    title: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[str] = None
    location: Optional[str] = None
    responsible_person: Optional[str] = None
    volunteers: Optional[str] = None
    budget: Optional[float] = None
    status: Optional[str] = None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    title: str
    event_date: date
    event_time: Optional[str] = None
    location: Optional[str]
    responsible_person: Optional[str]
    volunteers: Optional[str]
    budget: Optional[float]
    status: str


class AartiSlotCreate(BaseModel):
    slot_date: date
    session: str
    start_time: str
    notes: Optional[str] = None
    member_ids: list[int] = []


class AvailabilityUpdate(BaseModel):
    slot_id: int
    available: bool


class AartiAssignRequest(BaseModel):
    member_ids: list[int]


class AartiDayCreate(BaseModel):
    slot_date: date
    morning_time: str = "06:30"
    evening_time: str = "19:30"


class MahaprasadCreate(BaseModel):
    prasad_date: date
    menu: str
    expected_people: int = 0
    food_quantity: Optional[str] = None
    cooking_team: Optional[str] = None
    serving_team: Optional[str] = None
    volunteers: Optional[str] = None
    vendor: Optional[str] = None
    food_budget: float = 0
    actual_cost: Optional[float] = None
    distribution_time: Optional[str] = None


class MahaprasadUpdate(BaseModel):
    menu: Optional[str] = None
    expected_people: Optional[int] = None
    food_quantity: Optional[str] = None
    cooking_team: Optional[str] = None
    serving_team: Optional[str] = None
    volunteers: Optional[str] = None
    vendor: Optional[str] = None
    food_budget: Optional[float] = None
    actual_cost: Optional[float] = None
    distribution_time: Optional[str] = None


class InventoryCreate(BaseModel):
    name: str
    total_quantity: int
    used_quantity: int = 0
    returned_quantity: int = 0
    notes: Optional[str] = None


class DashboardOut(BaseModel):
    mandal_name: str
    vargani_collected: float
    vargani_pending: float
    vargani_expected: float
    expenses_spent: float
    balance: float
    today_morning_aarti: Optional[str]
    today_evening_aarti: Optional[str]
    today_mahaprasad: Optional[str]
    today_aarti_members: int
    upcoming_events: list[EventOut]
    announcements: list[AnnouncementOut]
