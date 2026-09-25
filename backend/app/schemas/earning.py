from pydantic import BaseModel


class EarningResponse(BaseModel):
    id: int
    worker_id: int
    payment_id: int
    amount: float
    earning_type: str

    model_config = {
        "from_attributes": True
    }


class EarningsSummary(BaseModel):
    worker_id: int
    total_earnings: float
    total_jobs: int