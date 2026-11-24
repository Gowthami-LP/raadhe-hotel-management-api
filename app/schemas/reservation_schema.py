from datetime import date, time

from pydantic import BaseModel, Field


class ReservationCreate(BaseModel):
    customer_name: str = Field(min_length=2)
    phone: str
    reservation_date: date
    reservation_time: time
    guests: int = Field(gt=0)
    table_number: int = Field(gt=0)


class ReservationStatusUpdate(BaseModel):
    status: str
