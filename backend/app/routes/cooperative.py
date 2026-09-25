from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.cooperative import Cooperative
from app.models.user import User, UserRole
from app.schemas.cooperative import (
    CooperativeCreate,
    CooperativeResponse,
)


router = APIRouter(
    prefix="/cooperatives",
    tags=["Cooperatives"]
)


@router.post(
    "/",
    response_model=CooperativeResponse
)
def create_cooperative(
    cooperative_data: CooperativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.COOPERATIVE_ADMIN
    ]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create cooperatives"
        )

    existing = db.query(Cooperative).filter(
        Cooperative.registration_number
        == cooperative_data.registration_number
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Cooperative already exists"
        )

    cooperative = Cooperative(
        **cooperative_data.model_dump()
    )

    db.add(cooperative)
    db.commit()
    db.refresh(cooperative)

    return cooperative