from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class CateringBookingCreate(BaseModel):
    customer_name: str = Field(min_length=2)
    phone: str
    event_type: Literal[
        "wedding",
        "birthday",
        "engagement",
        "corporate",
        "family_function",
        "other",
    ]
    event_date: date
    event_location: str
    guest_count: int = Field(gt=0)
    menu_items: list[str] = Field(min_length=1)
    price_per_person: float = Field(gt=0)


class CateringStatusUpdate(BaseModel):
    status: Literal[
        "requested",
        "quoted",
        "confirmed",
        "completed",
        "cancelled",
    ]
