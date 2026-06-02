import enum


class Category(str, enum.Enum):
    FOOD = "Food"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    ENTERTAINMENT = "Entertainment"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    OTHER = "Other"


class AlertType(str, enum.Enum):
    BUDGET_EXCEEDED = "budget_exceeded"
    BUDGET_THRESHOLD = "budget_threshold"  # 90% reached
    UNUSUAL_TRANSACTION = "unusual_transaction"
    SPENDING_INCREASE = "spending_increase"
