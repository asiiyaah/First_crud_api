from fastapi import APIRouter
from .schema import TriageRequest, TriageResponse

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest):
    # Stage 1: stub response.
    # Ollama will be connected in Stage 2.
    return TriageResponse(
        category="bug",
        priority="high",
        confidence=0.95,
        reason="Stub response for Stage 1 testing.",
    )