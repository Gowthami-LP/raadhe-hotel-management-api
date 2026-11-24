from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.connection import check_database_connection, client
from app.routes import (
    catering_routes,
    menu_routes,
    order_routes,
    payment_routes,
    reservation_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_database_connection()
    yield
    client.close()


app = FastAPI(
    title="Raadhe Hotel Management API",
    description="""
    Backend API for Raadhe Hotel, Chittoor.
    Features:
    - Food Menu Management
    - Customer Food Orders
    - Table Reservations
    - Catering Bookings
    - Billing Management
    """,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(menu_routes.router)
app.include_router(order_routes.router)
app.include_router(catering_routes.router)
app.include_router(reservation_routes.router)
app.include_router(payment_routes.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Raadhe Hotel Management API",
        "hotel": "Raadhe Hotel",
        "location": "Chittoor, Andhra Pradesh",
        "status": "Running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
    }
