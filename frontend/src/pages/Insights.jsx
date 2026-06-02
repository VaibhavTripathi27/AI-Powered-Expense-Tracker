import { insightService } from '../services/insightService'
import { useAsync } from '../hooks/useAsync'
import PageHeader from '../components/PageHeader.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'
import Spinner from '../components/ui/Spinner.jsx'

const categoryTone = {
  pattern: 'brand',
  savings: 'green',
  warning: 'red',
  recommendation: 'amber',
}

export default function Insights() {
  const { data, loading, error, refetch } = useAsync(() => insightService.get(), [])

  return (
    <div>
      <PageHeader
        title="AI-Powered Spending Insights"
        subtitle="Personalized analysis of your finances"
        action={
          <Button variant="secondary" onClick={refetch} loading={loading}>
            Regenerate
          </Button>
        }
      />

      {loading ? (
        <Card>
          <div className="flex flex-col items-center justify-center gap-3 py-12">
            <Spinner />
            <p className="text-sm text-slate-400">Analyzing your financial data…</p>
          </div>
        </Card>
      ) : error ? (
        <Card>
          <p className="py-8 text-center text-sm text-rose-500">{error}</p>
        </Card>
      ) : (
        <div className="space-y-4">
          <Card>
            <div className="mb-2 flex items-center gap-2">
              <span className="text-xl">🤖</span>
              <h3 className="font-semibold text-slate-800 dark:text-slate-100">
                Summary
              </h3>
              <Badge tone={data.generated_by === 'gemini' ? 'brand' : 'slate'}>
                {data.generated_by === 'gemini' ? 'Gemini 2.5 Pro' : 'Rule-based'}
              </Badge>
            </div>
            <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300">
              {data.summary}
            </p>
          </Card>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {data.insights.map((ins, i) => (
              <Card key={i}>
                <div className="mb-2 flex items-center justify-between">
                  <h4 className="font-semibold text-slate-800 dark:text-slate-100">
                    {ins.title}
                  </h4>
                  <Badge tone={categoryTone[ins.category] || 'slate'}>
                    {ins.category}
                  </Badge>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-300">
                  {ins.detail}
                </p>
              </Card>
            ))}
          </div>

          {data.recommendations?.length > 0 && (
            <Card title="Recommendations">
              <ul className="space-y-2">
                {data.recommendations.map((r, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-300"
                  >
                    <span className="text-brand-500">✓</span>
                    {r}
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
