# API Reference — AI Expense Tracker

Base URL: `{HOST}/api/v1`
Interactive docs (Swagger): `{HOST}/docs` · ReDoc: `{HOST}/redoc`

All endpoints except `/auth/register` and `/auth/login` require a Bearer token:

```
Authorization: Bearer <access_token>
```

---

## Authentication flow

1. `POST /auth/register` or `POST /auth/login` → returns `{ access_token, token_type, user }`.
2. Client stores the token (localStorage) and attaches it to every request.
3. `GET /auth/me` rehydrates the session on reload.
4. On `401`, the client clears the token and redirects to `/login`.

JWT is HS256-signed, contains `{ sub: <user_id>, exp, type: "access" }`, and expires
after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 24h).

---

## Auth

| Method | Path             | Body                          | Response                |
| ------ | ---------------- | ----------------------------- | ----------------------- |
| POST   | `/auth/register` | `{name, email, password}`     | `201` `AuthResponse`    |
| POST   | `/auth/login`    | `{email, password}`           | `200` `AuthResponse`    |
| GET    | `/auth/me`       | —                             | `200` `UserOut`         |
| POST   | `/auth/logout`   | —                             | `200` `{detail}`        |

**AuthResponse**: `{ access_token, token_type, user: { id, name, email, created_at } }`

---

## Expenses

| Method | Path                | Notes                                   |
| ------ | ------------------- | --------------------------------------- |
| GET    | `/expenses`         | Paginated + filterable (see params)     |
| POST   | `/expenses`         | Create — `201`                          |
| GET    | `/expenses/{id}`    | Single expense                          |
| PUT    | `/expenses/{id}`    | Partial update                          |
| DELETE | `/expenses/{id}`    | `204`                                   |

**Query params for `GET /expenses`:**
`page` (≥1), `page_size` (1–100), `category`, `start_date`, `end_date` (YYYY-MM-DD),
`search` (matches description/category).

**Paginated response:**
```json
{ "items": [ ... ], "total": 42, "page": 1, "page_size": 10, "pages": 5 }
```

**Expense body:** `{ amount: number>0, category: Category, description: string, transaction_date: "YYYY-MM-DD" }`

---

## Budgets

| Method | Path                    | Notes                                        |
| ------ | ----------------------- | -------------------------------------------- |
| GET    | `/budgets`              | List budgets                                 |
| GET    | `/budgets/utilization`  | Spent vs limit for the current month         |
| POST   | `/budgets`              | Create — `409` if category already budgeted  |
| PUT    | `/budgets/{id}`         | Update `monthly_limit`                        |
| DELETE | `/budgets/{id}`         | `204`                                        |

**BudgetUtilization:** `{ category, monthly_limit, spent, remaining, utilization_pct }`

---

## Alerts

| Method | Path                    | Notes                                  |
| ------ | ----------------------- | -------------------------------------- |
| GET    | `/alerts`               | `?unread_only=true` to filter          |
| PATCH  | `/alerts/{id}/read`     | Mark one read                          |
| PATCH  | `/alerts/read-all`      | Mark all read                          |
| DELETE | `/alerts/{id}`          | `204`                                  |

Alerts are generated server-side automatically when an expense is created.

---

## Analytics

| Method | Path                       | Response                       |
| ------ | -------------------------- | ------------------------------ |
| GET    | `/analytics/dashboard`     | `DashboardMetrics`             |
| GET    | `/analytics/health-score`  | `HealthScore` (0–100 + rating) |

**DashboardMetrics:** `{ total_expenses, monthly_expenses, category_breakdown[],
monthly_trend[], savings_estimate, total_budget, budget_utilization[] }`

**HealthScore:** `{ score, rating, savings_ratio, budget_adherence,
spending_consistency, breakdown }`

---

## AI Insights

| Method | Path        | Response          |
| ------ | ----------- | ----------------- |
| GET    | `/insights` | `InsightResponse` |

The backend aggregates an **anonymised** financial summary (never raw records),
sends it to Gemini 2.5 Pro, and returns:

```json
{
  "summary": "…",
  "insights": [ { "title": "…", "detail": "…", "category": "pattern|savings|warning|recommendation" } ],
  "recommendations": [ "…" ],
  "generated_by": "gemini"   // or "fallback" when GEMINI_API_KEY is unset
}
```

---

## Error format

All errors return `{ "detail": "message" }` with the appropriate status code
(`400`, `401`, `403`, `404`, `409`, `422`, `500`).
