from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ContentRequest(BaseModel):
    grade: int = Field(..., ge=1, le=12, description="Student grade level (1-12)")
    topic: str = Field(..., min_length=1, description="Topic to generate content for")


class MCQ(BaseModel):
    question: str
    options: List[str] = Field(..., min_length=4, max_length=4)
    answer: str

class GeneratorOutput(BaseModel):
    explanation: str
    mcqs: List[MCQ]


class ReviewerOutput(BaseModel):
    status: str = Field(..., pattern="^(pass|fail)$", description="pass or fail")
    feedback: List[str] = Field(default_factory=list)


class PipelineState(BaseModel):
    grade: int
    topic: str
    draft: Optional[GeneratorOutput] = None
    review: Optional[ReviewerOutput] = None
    refined: Optional[GeneratorOutput] = None
    feedback_for_refinement: Optional[List[str]] = None
    pass_number: int = 0
