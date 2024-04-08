"""Lesson 02: structured request bodies, Pydantic validation and API responses."""
from typing import Literal
from fastapi import FastAPI, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

app = FastAPI(title="Enrollment API | Validation")


class EnrollmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    student_name: str = Field(min_length=2, max_length=60)
    course_code: str = Field(min_length=3, max_length=12)
    semester: int = Field(ge=1, le=8)
    mode: Literal["online", "offline"]
    credits: int = Field(ge=1, le=6)

    @field_validator("course_code")
    @classmethod
    def normalize_course_code(cls, value: str) -> str:
        return value.upper()


class EnrollmentResponse(BaseModel):
    enrollment_id: str
    student_name: str
    course_code: str
    semester: int
    mode: str
    credits: int


@app.post("/enrollments/preview", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def preview_enrollment(payload: EnrollmentRequest):
    # This ID is for illustration only: there is no persistent enrollment store yet.
    return EnrollmentResponse(
        enrollment_id=f"PREVIEW-{payload.course_code}-{payload.semester}",
        **payload.model_dump(),
    )
