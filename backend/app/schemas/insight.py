from typing import List

from pydantic import BaseModel


class InsightItem(BaseModel):
    title: str
    detail: str
    category: str  # e.g. "pattern", "savings", "warning", "recommendation"


class InsightResponse(BaseModel):
    summary: str
    insights: List[InsightItem]
    recommendations: List[str]
    generated_by: str  # "gemini" or "fallback"
