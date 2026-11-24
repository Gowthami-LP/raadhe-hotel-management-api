from typing import Literal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    order_id: str
    amount: float = Field(gt=0)
    payment_method: Literal["cash", "upi", "card", "online"]
