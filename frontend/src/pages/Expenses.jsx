import { useEffect, useMemo, useState } from 'react'
import { expenseService } from '../services/expenseService'
import { useToast } from '../context/ToastContext.jsx'
import { CATEGORIES, CATEGORY_COLORS } from '../utils/constants'
import { formatCurrency, formatDate, todayISO } from '../utils/format'
import PageHeader from '../components/PageHeader.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Input from '../components/ui/Input.jsx'
import Select from '../components/ui/Select.jsx'
import Modal from '../components/ui/Modal.jsx'
import Badge from '../components/ui/Badge.jsx'
import Spinner from '../components/ui/Spinner.jsx'

const emptyForm = {
  amount: '',
  category: 'Food',
  description: '',
  transaction_date: todayISO(),
}

export default function Expenses() {
  const toast = useToast()
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    start_date: '',
    end_date: '',
    page: 1,
    page_size: 10,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)

  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    const params = Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v !== '' && v !== null),
    )
    expenseService
      .list(params)
      .then(setResult)
      .catch((e) => toast.error(e.message))
      .finally(() => setLoading(false))
  }

  // Debounce filter changes.
  useEffect(() => {
    const t = setTimeout(load, 300)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters])

  const openCreate = () => {
    setEditing(null)
    setForm(emptyForm)
    setModalOpen(true)
  }

  const openEdit = (exp) => {
    setEditing(exp)
    setForm({
      amount: exp.amount,
      category: exp.category,
      description: exp.description,
      transaction_date: exp.transaction_date,
    })
    setModalOpen(true)
  }

  const save = async (ev) => {
    ev.preventDefault()
    if (!form.amount || Number(form.amount) <= 0) {
      toast.error('Enter a valid amount')
      return
    }
    setSaving(true)
    const payload = { ...form, amount: Number(form.amount) }
    try {
      if (editing) {
        await expenseService.update(editing.id, payload)
        toast.success('Expense updated')
      } else {
        await expenseService.create(payload)
        toast.success('Expense added')
      }
      setModalOpen(false)
      load()
    } catch (e) {
      toast.error(e.message)
    } finally {
      setSaving(false)
    }
  }

  const remove = async (exp) => {
    if (!confirm('Delete this expense?')) return
    try {
      await expenseService.remove(exp.id)
      toast.success('Expense deleted')
      load()
    } catch (e) {
      toast.error(e.message)
    }
  }

  const totalPages = result?.pages || 1
  const setPage = (page) => setFilters((f) => ({ ...f, page }))
  const setFilter = (patch) => setFilters((f) => ({ ...f, ...patch, page: 1 }))

  const pageTotal = useMemo(
    () => (result?.items || []).reduce((s, e) => s + Number(e.amount), 0),
    [result],
  )

  return (
    <div>
      <PageHeader
        title="Expenses"
        subtitle="Create, filter and manage your transactions"
        action={<Button onClick={openCreate}>+ Add Expense</Button>}
      />

      <Card className="mb-4">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
          <Input
            label="Search"
            placeholder="Description or category"
            value={filters.search}
            onChange={(e) => setFilter({ search: e.target.value })}
          />
          <Select
            label="Category"
            value={filters.category}
            onChange={(e) => setFilter({ category: e.target.value })}
            options={[{ value: '', label: 'All categories' }, ...CATEGORIES]}
          />
          <Input
            label="From"
            type="date"
            value={filters.start_date}
            onChange={(e) => setFilter({ start_date: e.target.value })}
          />
          <Input
            label="To"
            type="date"
            value={filters.end_date}
            onChange={(e) => setFilter({ end_date: e.target.value })}
          />
        </div>
      </Card>

      <Card>
        {loading ? (
          <div className="flex h-40 items-center justify-center">
            <Spinner />
          </div>
        ) : result?.items?.length ? (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-200 text-xs uppercase text-slate-400 dark:border-slate-800">
                  <tr>
                    <th className="px-3 py-2">Date</th>
                    <th className="px-3 py-2">Category</th>
                    <th className="px-3 py-2">Description</th>
                    <th className="px-3 py-2 text-right">Amount</th>
                    <th className="px-3 py-2 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {result.items.map((exp) => (
                    <tr
                      key={exp.id}
                      className="border-b border-slate-100 last:border-0 dark:border-slate-800"
                    >
                      <td className="whitespace-nowrap px-3 py-3 text-slate-500 dark:text-slate-400">
                        {formatDate(exp.transaction_date)}
                      </td>
                      <td className="px-3 py-3">
                        <span className="inline-flex items-center gap-2">
                          <span
                            className="h-2.5 w-2.5 rounded-full"
                            style={{ background: CATEGORY_COLORS[exp.category] }}
                          />
                          {exp.category}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-slate-600 dark:text-slate-300">
                        {exp.description || '—'}
                      </td>
                      <td className="px-3 py-3 text-right font-semibold">
                        {formatCurrency(exp.amount)}
                      </td>
                      <td className="px-3 py-3 text-right">
                        <button
                          onClick={() => openEdit(exp)}
                          className="mr-3 text-brand-600 hover:underline"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => remove(exp)}
                          className="text-rose-600 hover:underline"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm">
              <div className="text-slate-500 dark:text-slate-400">
                {result.total} total · page sum{' '}
                <Badge tone="brand">{formatCurrency(pageTotal)}</Badge>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  className="px-3 py-1.5"
                  disabled={filters.page <= 1}
                  onClick={() => setPage(filters.page - 1)}
                >
                  Prev
                </Button>
                <span className="text-slate-500">
                  {filters.page} / {totalPages}
                </span>
                <Button
                  variant="secondary"
                  className="px-3 py-1.5"
                  disabled={filters.page >= totalPages}
                  onClick={() => setPage(filters.page + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          </>
        ) : (
          <p className="py-10 text-center text-sm text-slate-400">
            No expenses found. Add your first one!
          </p>
        )}
      </Card>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Edit Expense' : 'Add Expense'}
      >
        <form onSubmit={save} className="space-y-4">
          <Input
            label="Amount"
            type="number"
            step="0.01"
            min="0"
            value={form.amount}
            onChange={(e) => setForm({ ...form, amount: e.target.value })}
          />
          <Select
            label="Category"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
            options={CATEGORIES}
          />
          <Input
            label="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <Input
            label="Date"
            type="date"
            value={form.transaction_date}
            onChange={(e) => setForm({ ...form, transaction_date: e.target.value })}
          />
          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" loading={saving}>
              {editing ? 'Save' : 'Add'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
