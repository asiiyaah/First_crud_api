from fastapi import APIRouter

from .schema import TriageRequest, TriageResponse
from .service import triage_task


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest):
    return triage_task(request.text)