from math import radians, sin, cos, sqrt, atan2

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.worker import Worker
from app.models.worker_skill import WorkerSkill
from app.models.service import Service
from app.schemas.search import WorkerSearchResponse


router = APIRouter(
    prefix="/search",
    tags=["Worker Search"]
)


def calculate_distance(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate distance between two coordinates
    using the Haversine formula.

    Returns distance in kilometers.
    """

    earth_radius = 6371.0

    lat1 = radians(latitude1)
    lon1 = radians(longitude1)

    lat2 = radians(latitude2)
    lon2 = radians(longitude2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c


@router.get(
    "/workers",
    response_model=list[WorkerSearchResponse]
)
def search_workers(
    service_id: int | None = Query(default=None),

    latitude: float | None = Query(default=None),

    longitude: float | None = Query(default=None),

    radius_km: float = Query(
        default=10,
        gt=0,
        le=100
    ),

    available_only: bool = Query(default=True),

    db: Session = Depends(get_db)
):
    query = (
        select(
            Worker.id.label("worker_id"),
            Worker.user_id,
            User.name,
            Service.id.label("service_id"),
            Service.name.label("service_name"),
            WorkerSkill.skill_level,
            WorkerSkill.years_experience,
            Worker.hourly_rate,
            Worker.latitude,
            Worker.longitude,
            Worker.availability,
            Worker.verification_status,
            Worker.average_rating,
            Worker.total_jobs
        )
        .join(
            User,
            User.id == Worker.user_id
        )
        .join(
            WorkerSkill,
            WorkerSkill.worker_id == Worker.id
        )
        .join(
            Service,
            Service.id == WorkerSkill.service_id
        )
    )

    if service_id is not None:
        query = query.where(
            Service.id == service_id
        )

    if available_only:
        query = query.where(
            Worker.availability == True
        )

    results = db.execute(query).all()

    response = []

    for row in results:

        # If customer location is provided,
        # workers without coordinates are skipped.
        if latitude is not None and longitude is not None:

            if row.latitude is None or row.longitude is None:
                continue

            distance = calculate_distance(
                latitude,
                longitude,
                row.latitude,
                row.longitude
            )

            # Ignore workers outside requested radius
            if distance > radius_km:
                continue

        else:
            distance = None

        response.append(
            WorkerSearchResponse(

    worker_id=row.worker_id,
    user_id=row.user_id,
    name=row.name,
    service_id=row.service_id,
    service_name=row.service_name,
    skill_level=row.skill_level.value,
    years_experience=row.years_experience,
    hourly_rate=row.hourly_rate,
    latitude=row.latitude,
    longitude=row.longitude,
    distance_km=round(distance, 2) if distance is not None else None,
    availability=row.availability,
    verification_status=row.verification_status.value,
    average_rating=row.average_rating,
    total_jobs=row.total_jobs

            )
        )

    # If customer location is provided,
    # sort workers by nearest first.
    if latitude is not None and longitude is not None:

        def get_distance(worker):
            if worker.latitude is None or worker.longitude is None:
                return float("inf")

            return calculate_distance(
                latitude,
                longitude,
                worker.latitude,
                worker.longitude
            )

        response.sort(
            key=get_distance
        )

    return response