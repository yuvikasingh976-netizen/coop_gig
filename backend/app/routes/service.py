from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.service import Service
from app.models.user import User, UserRole
from app.schemas.service import (
    ServiceCreate,
    ServiceResponse,
)


router = APIRouter(
    prefix="/services",
    tags=["Services"]
)


@router.post(
    "/",
    response_model=ServiceResponse
)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.COOPERATIVE_ADMIN
    ]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create services"
        )

    existing = db.scalar(
        select(Service).where(
            Service.name == service_data.name
        )
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Service already exists"
        )

    service = Service(
        **service_data.model_dump()
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service


@router.get(
    "/",
    response_model=list[ServiceResponse]
)
def get_services(
    db: Session = Depends(get_db)
):

    services = db.scalars(
        select(Service).where(
            Service.is_active == True
        )
    ).all()

    return services