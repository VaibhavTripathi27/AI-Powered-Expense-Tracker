import { CATEGORY_COLORS } from '../../utils/constants'
import { formatCurrency } from '../../utils/format'

function barColor(pct) {
  if (pct >= 100) return 'bg-rose-500'
  if (pct >= 90) return 'bg-amber-500'
  return 'bg-emerald-500'
}

export default function BudgetProgress({ items = [] }) {
  if (!items.length) {
    return (
      <p className="py-6 text-center text-sm text-slate-400">
        No budgets configured yet.
      </p>
    )
  }

  return (
    <div className="space-y-4">
      {items.map((b) => {
        const pct = Math.min(b.utilization_pct, 100)
        return (
          <div key={b.category}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 font-medium text-slate-700 dark:text-slate-200">
                <span
                  className="inline-block h-2.5 w-2.5 rounded-full"
                  style={{ background: CATEGORY_COLORS[b.category] }}
                />
                {b.category}
              </span>
              <span className="text-slate-500 dark:text-slate-400">
                {formatCurrency(b.spent)} / {formatCurrency(b.monthly_limit)}
              </span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
              <div
                className={`h-full rounded-full ${barColor(b.utilization_pct)}`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <div className="mt-1 text-right text-xs text-slate-400">
              {b.utilization_pct.toFixed(0)}% used
            </div>
          </div>
        )
      })}
    </div>
  )
}
