import enum

class Role(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    client = "client"

class CustomerStatus(str, enum.Enum):
    active = "Active"
    inactive = "Inactive"

class RoomStatus(str, enum.Enum):
    empty = "EMPTY"
    occupied = "OCCUPIED"
    stopped = "STOPPED"

class PaymentType(str, enum.Enum):
    full = "FULL"
    partial = "PARTIAL"

# ✅ NEW 4 statuses
class PaymentStatus(str, enum.Enum):
    opening = "OPENING"
    in_progress = "IN_PROGRESS"
    accepted = "ACCEPTED"
    debt = "DEBT"

class IssueType(str, enum.Enum):
    electricity = "Electricity"
    water = "Water"
    door = "Door"
    other = "Other"

class IssueStatus(str, enum.Enum):
    opening = "OPENING"
    accepted = "ACCEPTED"
    resolved = "RESOLVED"


