import { analyticsService } from '../services/analyticsService'
import { useAsync } from '../hooks/useAsync'
import PageHeader from '../components/PageHeader.jsx'
import StatCard from '../components/StatCard.jsx'
import Card from '../components/ui/Card.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import HealthScoreCard from '../components/HealthScoreCard.jsx'
import CategoryPieChart from '../components/charts/CategoryPieChart.jsx'
import SpendingLineChart from '../components/charts/SpendingLineChart.jsx'
import MonthlyBarChart from '../components/charts/MonthlyBarChart.jsx'
import BudgetProgress from '../components/charts/BudgetProgress.jsx'
import { formatCurrency } from '../utils/format'

export default function Dashboard() {
  const { data, loading, error } = useAsync(
    () =>
      Promise.all([
        analyticsService.dashboard(),
        analyticsService.healthScore(),
      ]).then(([dashboard, health]) => ({ dashboard, health })),
    [],
  )

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return <p className="text-sm text-rose-500">{error}</p>
  }

  const { dashboard, health } = data

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Your financial overview at a glance"
      />

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Expenses"
          value={formatCurrency(dashboard.total_expenses)}
          sub="All time"
        />
        <StatCard
          label="This Month"
          value={formatCurrency(dashboard.monthly_expenses)}
          accent="amber"
        />
        <StatCard
          label="Monthly Budget"
          value={formatCurrency(dashboard.total_budget)}
          accent="brand"
        />
        <StatCard
          label="Est. Savings"
          value={formatCurrency(dashboard.savings_estimate)}
          accent={dashboard.savings_estimate >= 0 ? 'green' : 'red'}
          sub="Budget minus spend"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Spending by Category (This Month)" className="lg:col-span-2">
          <CategoryPieChart data={dashboard.category_breakdown} />
        </Card>
        <HealthScoreCard data={health} />
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Spending Trend (6 months)">
          <SpendingLineChart data={dashboard.monthly_trend} />
        </Card>
        <Card title="Monthly Spending">
          <MonthlyBarChart data={dashboard.monthly_trend} />
        </Card>
      </div>

      <div className="mt-4">
        <Card title="Budget Utilization">
          <BudgetProgress items={dashboard.budget_utilization} />
        </Card>
      </div>
    </div>
  )
}
