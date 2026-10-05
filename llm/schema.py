from pydantic import BaseModel, Field
from typing import Literal


class TriageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class TriageResponse(BaseModel):
    category: Literal["bug", "feature", "task", "other"]
    priority: Literal["low", "normal", "high"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., min_length=1, max_length=500)