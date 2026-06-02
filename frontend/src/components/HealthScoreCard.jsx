function ratingTone(score) {
  if (score >= 80) return { ring: '#10b981', text: 'text-emerald-600' }
  if (score >= 65) return { ring: '#22c55e', text: 'text-green-600' }
  if (score >= 50) return { ring: '#f59e0b', text: 'text-amber-600' }
  if (score >= 35) return { ring: '#f97316', text: 'text-orange-600' }
  return { ring: '#ef4444', text: 'text-rose-600' }
}

export default function HealthScoreCard({ data }) {
  if (!data) return null
  const tone = ratingTone(data.score)
  const circumference = 2 * Math.PI * 52
  const offset = circumference - (data.score / 100) * circumference

  return (
    <div className="card flex flex-col items-center">
      <h3 className="mb-3 self-start text-sm font-semibold text-slate-700 dark:text-slate-200">
        Financial Health Score
      </h3>
      <div className="relative h-36 w-36">
        <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r="52"
            fill="none"
            strokeWidth="12"
            className="stroke-slate-200 dark:stroke-slate-800"
          />
          <circle
            cx="60"
            cy="60"
            r="52"
            fill="none"
            strokeWidth="12"
            strokeLinecap="round"
            stroke={tone.ring}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold ${tone.text}`}>{data.score}</span>
          <span className="text-xs text-slate-400">/ 100</span>
        </div>
      </div>
      <p className={`mt-3 text-lg font-semibold ${tone.text}`}>{data.rating}</p>
      <div className="mt-4 grid w-full grid-cols-3 gap-2 text-center text-xs">
        <Pillar label="Savings" value={data.breakdown.savings_points} />
        <Pillar label="Adherence" value={data.breakdown.adherence_points} />
        <Pillar label="Consistency" value={data.breakdown.consistency_points} />
      </div>
    </div>
  )
}

function Pillar({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-50 py-2 dark:bg-slate-800">
      <p className="font-semibold text-slate-700 dark:text-slate-200">{value}</p>
      <p className="text-slate-400">{label}</p>
    </div>
  )
}
