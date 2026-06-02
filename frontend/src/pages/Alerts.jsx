import { alertService } from '../services/alertService'
import { useAsync } from '../hooks/useAsync'
import { useToast } from '../context/ToastContext.jsx'
import { ALERT_LABELS } from '../utils/constants'
import { formatDateTime } from '../utils/format'
import PageHeader from '../components/PageHeader.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Badge from '../components/ui/Badge.jsx'
import Spinner from '../components/ui/Spinner.jsx'

const toneFor = (type) =>
  type === 'budget_exceeded'
    ? 'red'
    : type === 'budget_threshold'
      ? 'amber'
      : type === 'unusual_transaction'
        ? 'brand'
        : 'slate'

export default function Alerts() {
  const toast = useToast()
  const { data, loading, refetch, setData } = useAsync(() => alertService.list(), [])

  const markRead = async (alert) => {
    try {
      await alertService.markRead(alert.id)
      setData((prev) =>
        prev.map((a) => (a.id === alert.id ? { ...a, is_read: true } : a)),
      )
    } catch (e) {
      toast.error(e.message)
    }
  }

  const markAll = async () => {
    try {
      await alertService.markAllRead()
      toast.success('All alerts marked as read')
      refetch()
    } catch (e) {
      toast.error(e.message)
    }
  }

  const remove = async (alert) => {
    try {
      await alertService.remove(alert.id)
      setData((prev) => prev.filter((a) => a.id !== alert.id))
    } catch (e) {
      toast.error(e.message)
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner />
      </div>
    )
  }

  const unread = data.filter((a) => !a.is_read).length

  return (
    <div>
      <PageHeader
        title="Alerts"
        subtitle={unread ? `${unread} unread` : 'You are all caught up'}
        action={
          data.length > 0 && (
            <Button variant="secondary" onClick={markAll}>
              Mark all read
            </Button>
          )
        }
      />

      {data.length === 0 ? (
        <Card>
          <p className="py-10 text-center text-sm text-slate-400">
            🎉 No alerts. Spend within your budgets to keep it that way!
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {data.map((a) => (
            <Card
              key={a.id}
              className={a.is_read ? 'opacity-70' : 'border-l-4 border-l-brand-500'}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="mb-1 flex items-center gap-2">
                    <Badge tone={toneFor(a.type)}>
                      {ALERT_LABELS[a.type] || a.type}
                    </Badge>
                    {!a.is_read && <Badge tone="green">New</Badge>}
                  </div>
                  <p className="text-sm text-slate-700 dark:text-slate-200">
                    {a.message}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    {formatDateTime(a.created_at)}
                  </p>
                </div>
                <div className="flex shrink-0 flex-col gap-1 text-right text-sm">
                  {!a.is_read && (
                    <button
                      onClick={() => markRead(a)}
                      className="text-brand-600 hover:underline"
                    >
                      Mark read
                    </button>
                  )}
                  <button
                    onClick={() => remove(a)}
                    className="text-rose-600 hover:underline"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
