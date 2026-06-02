import { ResponsiveLine } from '@nivo/line'
import { useTheme } from '../../context/ThemeContext.jsx'
import { formatCurrency } from '../../utils/format'

export default function SpendingLineChart({ data }) {
  const { theme } = useTheme()
  const text = theme === 'dark' ? '#cbd5e1' : '#475569'
  const grid = theme === 'dark' ? '#1e293b' : '#e2e8f0'

  if (!data?.length) return <Empty />

  const series = [
    {
      id: 'Spending',
      data: data.map((d) => ({ x: d.month, y: Number(d.amount) })),
    },
  ]

  return (
    <div className="h-72">
      <ResponsiveLine
        data={series}
        margin={{ top: 20, right: 24, bottom: 50, left: 60 }}
        xScale={{ type: 'point' }}
        yScale={{ type: 'linear', min: 0, max: 'auto' }}
        curve="monotoneX"
        colors={['#6366f1']}
        lineWidth={3}
        pointSize={8}
        pointColor="#6366f1"
        pointBorderWidth={2}
        pointBorderColor="#fff"
        enableArea
        areaOpacity={0.1}
        axisBottom={{ tickRotation: -35 }}
        axisLeft={{ format: (v) => formatCurrency(v) }}
        enableGridX={false}
        theme={{
          text: { fill: text },
          axis: { ticks: { text: { fill: text } } },
          grid: { line: { stroke: grid } },
          tooltip: { container: { color: '#0f172a' } },
        }}
        useMesh
      />
    </div>
  )
}

function Empty() {
  return (
    <div className="flex h-72 items-center justify-center text-sm text-slate-400">
      Not enough data to show a trend
    </div>
  )
}
