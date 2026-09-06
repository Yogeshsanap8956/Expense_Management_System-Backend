from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    TREASURER = "treasurer"
    AARTI_COORDINATOR = "aarti_coordinator"
    PRASAD_COORDINATOR = "prasad_coordinator"
    MEMBER = "member"


class PaymentMethod(str, Enum):
    CASH = "cash"
    UPI = "upi"


class ExpenseCategory(str, Enum):
    DECORATION = "decoration"
    SOUND_SYSTEM = "sound_system"
    LIGHTING = "lighting"
    GANPATI_IDOL = "ganpati_idol"
    PRASAD = "prasad"
    FLOWERS = "flowers"
    POOJA_MATERIAL = "pooja_material"
    CLEANING = "cleaning"
    ELECTRICITY = "electricity"
    TRANSPORTATION = "transportation"
    CULTURAL_PROGRAMS = "cultural_programs"
    OTHER = "other"


class AartiSession(str, Enum):
    MORNING = "morning"
    EVENING = "evening"


class EventStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class InventoryStatus(str, Enum):
    AVAILABLE = "available"
    USED = "used"
    RETURNED = "returned"
