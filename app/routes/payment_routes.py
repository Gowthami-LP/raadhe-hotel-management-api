from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from app.database.connection import database
from app.schemas.payment_schema import PaymentCreate


router = APIRouter(prefix="/payments", tags=["Billing and Payments"])
orders_collection = database["food_orders"]
payments_collection = database["payments"]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentCreate):
    if not ObjectId.is_valid(payment.order_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID",
        )

    order = orders_collection.find_one(
        {"_id": ObjectId(payment.order_id)}
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    payment_data = payment.model_dump()
    payment_data["created_at"] = datetime.now(timezone.utc)
    result = payments_collection.insert_one(payment_data)
    payment_data.pop("_id", None)
    payment_data["id"] = str(result.inserted_id)
    return payment_data
