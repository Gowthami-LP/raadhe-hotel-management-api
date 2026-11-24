from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from pymongo import ReturnDocument

from app.database.connection import database
from app.schemas.catering_schema import (
    CateringBookingCreate,
    CateringStatusUpdate,
)


router = APIRouter(prefix="/catering", tags=["Catering Management"])
catering_collection = database["catering_bookings"]


def convert_booking(booking):
    booking["id"] = str(booking.pop("_id"))
    return booking


def parse_object_id(booking_id: str) -> ObjectId:
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid catering booking ID",
        )
    return ObjectId(booking_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_catering_booking(booking: CateringBookingCreate):
    total_amount = booking.guest_count * booking.price_per_person
    booking_data = booking.model_dump()
    booking_data["event_date"] = booking.event_date.isoformat()
    booking_data["estimated_total"] = round(total_amount, 2)
    booking_data["status"] = "requested"
    booking_data["created_at"] = datetime.now(timezone.utc)

    result = catering_collection.insert_one(booking_data)
    booking_data["_id"] = result.inserted_id
    return convert_booking(booking_data)


@router.get("/")
def get_catering_bookings():
    return [convert_booking(booking) for booking in catering_collection.find()]


@router.get("/{booking_id}")
def get_catering_booking(booking_id: str):
    booking = catering_collection.find_one(
        {"_id": parse_object_id(booking_id)}
    )
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catering booking not found",
        )
    return convert_booking(booking)


@router.patch("/{booking_id}/status")
def update_catering_status(
    booking_id: str,
    booking_status: CateringStatusUpdate,
):
    booking = catering_collection.find_one_and_update(
        {"_id": parse_object_id(booking_id)},
        {"$set": {"status": booking_status.status}},
        return_document=ReturnDocument.AFTER,
    )
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Catering booking not found",
        )
    return convert_booking(booking)
