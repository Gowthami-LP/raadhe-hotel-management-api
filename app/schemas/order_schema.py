from typing import Literal

from pydantic import BaseModel, Field


class OrderItemRequest(BaseModel):
    menu_item_id: str
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2)
    phone: str
    order_type: Literal["dine_in", "takeaway", "delivery"]
    table_number: int | None = None
    items: list[OrderItemRequest] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: Literal[
        "placed",
        "confirmed",
        "preparing",
        "ready",
        "completed",
        "cancelled",
    ]
