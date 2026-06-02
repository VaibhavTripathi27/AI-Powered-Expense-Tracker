import { ResponsiveBar } from '@nivo/bar'
import { useTheme } from '../../context/ThemeContext.jsx'
import { formatCurrency } from '../../utils/format'

export default function MonthlyBarChart({ data }) {
  const { theme } = useTheme()
  const text = theme === 'dark' ? '#cbd5e1' : '#475569'
  const grid = theme === 'dark' ? '#1e293b' : '#e2e8f0'

  if (!data?.length) return <Empty />

  const chartData = data.map((d) => ({ month: d.month, amount: Number(d.amount) }))

  return (
    <div className="h-72">
      <ResponsiveBar
        data={chartData}
        keys={['amount']}
        indexBy="month"
        margin={{ top: 20, right: 24, bottom: 50, left: 60 }}
        padding={0.35}
        colors={['#4f46e5']}
        borderRadius={6}
        axisBottom={{ tickRotation: -35 }}
        axisLeft={{ format: (v) => formatCurrency(v) }}
        enableLabel={false}
        valueFormat={(v) => formatCurrency(v)}
        theme={{
          text: { fill: text },
          axis: { ticks: { text: { fill: text } } },
          grid: { line: { stroke: grid } },
          tooltip: { container: { color: '#0f172a' } },
        }}
      />
    </div>
  )
}

function Empty() {
  return (
    <div className="flex h-72 items-center justify-center text-sm text-slate-400">
      No monthly data yet
    </div>
  )
}
