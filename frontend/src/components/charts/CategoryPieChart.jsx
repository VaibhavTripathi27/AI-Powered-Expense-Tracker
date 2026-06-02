import { ResponsivePie } from '@nivo/pie'
import { useTheme } from '../../context/ThemeContext.jsx'
import { CATEGORY_COLORS } from '../../utils/constants'
import { formatCurrency } from '../../utils/format'

export default function CategoryPieChart({ data }) {
  const { theme } = useTheme()
  const text = theme === 'dark' ? '#cbd5e1' : '#475569'

  if (!data?.length) return <Empty />

  const chartData = data.map((d) => ({
    id: d.category,
    label: d.category,
    value: Number(d.amount),
    color: CATEGORY_COLORS[d.category] || '#64748b',
  }))

  return (
    <div className="h-72">
      <ResponsivePie
        data={chartData}
        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
        innerRadius={0.6}
        padAngle={1}
        cornerRadius={4}
        colors={{ datum: 'data.color' }}
        borderWidth={0}
        enableArcLinkLabels={false}
        arcLabelsSkipAngle={12}
        arcLabelsTextColor="#fff"
        valueFormat={(v) => formatCurrency(v)}
        theme={{ text: { fill: text }, tooltip: { container: { color: '#0f172a' } } }}
        legends={[
          {
            anchor: 'bottom',
            direction: 'row',
            translateY: 10,
            itemWidth: 70,
            itemHeight: 16,
            symbolSize: 10,
            symbolShape: 'circle',
            itemTextColor: text,
          },
        ]}
      />
    </div>
  )
}

function Empty() {
  return (
    <div className="flex h-72 items-center justify-center text-sm text-slate-400">
      No spending data yet
    </div>
  )
}
