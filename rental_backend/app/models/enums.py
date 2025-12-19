import enum

class Role(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    client = "client"

class PaymentType(str, enum.Enum):
    full = "FULL"
    partial = "PARTIAL"

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
