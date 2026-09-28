from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):
    user_id: int = Field(ge=1, le=2_147_483_647)
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, lt=500)
    goal: str = Field(min_length=2, max_length=200)
    intensity: Literal["low", "medium", "high"]

    @field_validator("name", "goal")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value


class FeedbackRequest(BaseModel):
    user_id: int = Field(ge=1)
    feedback: str = Field(min_length=5, max_length=2_000)

    @field_validator("feedback")
    @classmethod
    def strip_feedback(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Feedback cannot be blank")
        return value


class PlanResponse(BaseModel):
    user_id: int
    name: str
    age: int
    weight: float
    goal: str
    intensity: str
    workout_plan: str
    nutrition_tip: str
    updated_plan: str | None = None


class FeedbackResponse(BaseModel):
    message: str
    updated_plan: str
