from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.database import Base, engine


# =========================================================
# IMPORT MODELS
# =========================================================

from app.models.user import User
from app.models.cooperative import Cooperative
from app.models.worker import Worker
from app.models.service import Service
from app.models.worker_skill import WorkerSkill
from app.models.certification import Certification
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.review import Review
from app.models.earning import WorkerEarning
from app.models.welfare import WorkerWelfare


# =========================================================
# IMPORT ROUTES
# =========================================================

from app.routes.auth import router as auth_router
from app.routes.cooperative import router as cooperative_router
from app.routes.worker import router as worker_router
from app.routes.service import router as service_router
from app.routes.worker_skill import router as worker_skill_router
from app.routes.certification import router as certification_router
from app.routes.search import router as search_router
from app.routes.booking import router as booking_router
from app.routes.payment import router as payment_router
from app.routes.review import router as review_router
from app.routes.welfare import router as welfare_router

from app.routes.admin import router as admin_router
from app.routes.admin_workers import router as admin_workers_router
from app.routes.admin_bookings import router as admin_bookings_router
from app.routes.admin_payments import router as admin_payments_router
from app.routes.admin_reviews import router as admin_reviews_router

from app.routes.cooperative_admin import (
    router as cooperative_admin_router
)


# =========================================================
# CREATE FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="coop_gig",
    description="Digital service marketplace for Labour Cooperatives",
    version="1.0.0"
)


# =========================================================
# DATABASE TABLE CREATION
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# SERVE FRONTEND
# =========================================================

frontend_path = Path(__file__).resolve().parents[2] / "frontend"

app.mount(
    "/ui",
    StaticFiles(
        directory=frontend_path,
        html=True
    ),
    name="frontend"
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(auth_router)

app.include_router(cooperative_router)

app.include_router(worker_router)

app.include_router(service_router)

app.include_router(worker_skill_router)

app.include_router(certification_router)

app.include_router(search_router)

app.include_router(booking_router)

app.include_router(payment_router)

app.include_router(review_router)

app.include_router(welfare_router)


# =========================================================
# ADMIN ROUTES
# =========================================================

app.include_router(admin_router)

app.include_router(admin_workers_router)

app.include_router(admin_bookings_router)

app.include_router(admin_payments_router)

app.include_router(admin_reviews_router)


# =========================================================
# COOPERATIVE ADMIN ROUTES
# =========================================================

app.include_router(cooperative_admin_router)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "coop_gig API is running",
        "status": "success"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# =========================================================
# DATABASE TEST
# =========================================================

@app.get("/database-test")
def database_test():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            value = result.scalar()

        return {
            "database": "connected",
            "test_result": value
        }

    except Exception as e:

        return {
            "database": "connection failed",
            "error": str(e)
        }