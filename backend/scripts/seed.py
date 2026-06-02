"""Seed the database with a demo user, budgets and expenses.

Usage:  python -m scripts.seed
"""
import random
from datetime import date, timedelta

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.budget import Budget
from app.models.enums import Category
from app.models.expense import Expense
from app.models.user import User

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo12345"


def run() -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if not user:
            user = User(
                name="Demo User",
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        if not db.query(Budget).filter(Budget.user_id == user.id).first():
            limits = {
                Category.FOOD: 500,
                Category.TRAVEL: 300,
                Category.SHOPPING: 400,
                Category.BILLS: 600,
                Category.ENTERTAINMENT: 200,
            }
            for cat, limit in limits.items():
                db.add(
                    Budget(category=cat.value, monthly_limit=limit, user_id=user.id)
                )
            db.commit()

        if not db.query(Expense).filter(Expense.user_id == user.id).first():
            categories = list(Category)
            today = date.today()
            for _ in range(120):
                day = today - timedelta(days=random.randint(0, 150))
                cat = random.choice(categories)
                db.add(
                    Expense(
                        amount=round(random.uniform(5, 250), 2),
                        category=cat.value,
                        description=f"{cat.value} purchase",
                        transaction_date=day,
                        user_id=user.id,
                    )
                )
            db.commit()

        print(f"Seeded demo user -> {DEMO_EMAIL} / {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
