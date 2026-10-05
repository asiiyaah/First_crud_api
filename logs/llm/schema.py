from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TriageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(..., min_length=1, max_length=2000)

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("String should contain at least one non-whitespace character")
        return value


class TriageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Literal["bug", "feature", "task", "other"]
    priority: Literal["low", "normal", "high"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., min_length=1, max_length=500)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("reason must not be blank")
        return value
