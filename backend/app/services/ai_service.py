import json
import logging
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.insight import InsightItem, InsightResponse
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a professional personal-finance advisor.
You will be given an AGGREGATED, anonymised financial summary (never raw transactions).
Analyse it and return STRICT JSON only, matching this schema:

{
  "summary": "2-3 sentence overview of the user's financial situation",
  "insights": [
    {"title": "short title", "detail": "1-2 sentences", "category": "pattern|savings|warning|recommendation"}
  ],
  "recommendations": ["actionable suggestion", "..."]
}

Provide 4-6 insights and 3-5 recommendations. Be specific, reference the numbers,
and keep a supportive, practical tone. Output JSON only, no markdown fences."""


class AIService:
    """Dedicated AI layer. Aggregates user data into a privacy-safe summary,
    sends it to Gemini, and returns structured insights. Falls back to a
    rule-based generator when Gemini is unavailable."""

    def __init__(self, db: Session):
        self.analytics = AnalyticsService(db)

    def build_summary(self, user_id: int) -> Dict[str, Any]:
        """Aggregate financial data into a structured, anonymised summary.
        No raw database records (descriptions, ids, dates) are ever included."""
        dashboard = self.analytics.dashboard(user_id)
        health = self.analytics.health_score(user_id)
        return {
            "currency": "generic units",
            "total_expenses_all_time": dashboard.total_expenses,
            "expenses_this_month": dashboard.monthly_expenses,
            "estimated_monthly_savings": dashboard.savings_estimate,
            "total_monthly_budget": dashboard.total_budget,
            "spending_by_category_this_month": [
                {"category": c.category, "amount": c.amount}
                for c in dashboard.category_breakdown
            ],
            "monthly_spending_trend": [
                {"month": m.month, "amount": m.amount} for m in dashboard.monthly_trend
            ],
            "budget_utilization": [
                {
                    "category": b.category,
                    "limit": b.monthly_limit,
                    "spent": b.spent,
                    "utilization_pct": b.utilization_pct,
                }
                for b in dashboard.budget_utilization
            ],
            "financial_health_score": health.score,
            "health_rating": health.rating,
        }

    def generate_insights(self, user_id: int) -> InsightResponse:
        summary = self.build_summary(user_id)

        if settings.GEMINI_API_KEY:
            try:
                return self._generate_with_gemini(summary)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Gemini insight generation failed: %s", exc)

        return self._fallback(summary)

    # ------------------------------------------------------------------ #
    def _generate_with_gemini(self, summary: Dict[str, Any]) -> InsightResponse:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            settings.GEMINI_MODEL, system_instruction=SYSTEM_PROMPT
        )
        prompt = "Financial summary:\n" + json.dumps(summary, indent=2)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        data = json.loads(response.text)
        print("nnnnnnnn", data)
        return InsightResponse(
            summary=data.get("summary", ""),
            insights=[InsightItem(**i) for i in data.get("insights", [])],
            recommendations=data.get("recommendations", []),
            generated_by="gemini",
        )

    # ------------------------------------------------------------------ #
    def _fallback(self, summary: Dict[str, Any]) -> InsightResponse:
        insights: list[InsightItem] = []
        recommendations: list[str] = []

        categories = summary["spending_by_category_this_month"]
        if categories:
            top = categories[0]
            insights.append(
                InsightItem(
                    title="Top spending category",
                    detail=f"{top['category']} is your largest category this month "
                    f"at {top['amount']:.2f}.",
                    category="pattern",
                )
            )

        for b in summary["budget_utilization"]:
            if b["utilization_pct"] >= 100:
                insights.append(
                    InsightItem(
                        title=f"{b['category']} budget exceeded",
                        detail=f"You've spent {b['spent']:.2f} against a "
                        f"{b['limit']:.2f} limit ({b['utilization_pct']:.0f}%).",
                        category="warning",
                    )
                )
                recommendations.append(
                    f"Reduce {b['category']} spending to get back within budget."
                )
            elif b["utilization_pct"] >= 90:
                insights.append(
                    InsightItem(
                        title=f"{b['category']} budget nearly used",
                        detail=f"{b['utilization_pct']:.0f}% of your {b['category']} "
                        "budget is gone.",
                        category="warning",
                    )
                )

        savings = summary["estimated_monthly_savings"]
        if savings > 0:
            insights.append(
                InsightItem(
                    title="On track to save",
                    detail=f"You're estimated to save {savings:.2f} this month "
                    "against your budgets.",
                    category="savings",
                )
            )
        elif summary["total_monthly_budget"] > 0:
            insights.append(
                InsightItem(
                    title="Spending over budget",
                    detail="Your spending currently exceeds your total monthly budget.",
                    category="warning",
                )
            )

        score = summary["financial_health_score"]
        insights.append(
            InsightItem(
                title="Financial health",
                detail=f"Your financial health score is {score}/100 "
                f"({summary['health_rating']}).",
                category="recommendation",
            )
        )

        if not recommendations:
            recommendations = [
                "Set monthly budgets for your top spending categories.",
                "Aim to keep each category under 90% of its budget.",
                "Review your largest expenses weekly to catch overspending early.",
            ]

        return InsightResponse(
            summary=f"You've spent {summary['expenses_this_month']:.2f} this month "
            f"with a financial health score of {score}/100 "
            f"({summary['health_rating']}).",
            insights=insights,
            recommendations=recommendations,
            generated_by="fallback",
        )
