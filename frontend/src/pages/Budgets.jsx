import { useState } from 'react'
import { budgetService } from '../services/budgetService'
import { useAsync } from '../hooks/useAsync'
import { useToast } from '../context/ToastContext.jsx'
import { CATEGORIES } from '../utils/constants'
import { formatCurrency } from '../utils/format'
import PageHeader from '../components/PageHeader.jsx'
import Card from '../components/ui/Card.jsx'
import Button from '../components/ui/Button.jsx'
import Input from '../components/ui/Input.jsx'
import Select from '../components/ui/Select.jsx'
import Modal from '../components/ui/Modal.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import BudgetProgress from '../components/charts/BudgetProgress.jsx'

export default function Budgets() {
  const toast = useToast()
  const { data, loading, refetch } = useAsync(
    () =>
      Promise.all([budgetService.list(), budgetService.utilization()]).then(
        ([budgets, utilization]) => ({ budgets, utilization }),
      ),
    [],
  )

  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ category: 'Food', monthly_limit: '' })
  const [saving, setSaving] = useState(false)

  const openCreate = () => {
    setEditing(null)
    setForm({ category: 'Food', monthly_limit: '' })
    setModalOpen(true)
  }

  const openEdit = (b) => {
    setEditing(b)
    setForm({ category: b.category, monthly_limit: b.monthly_limit })
    setModalOpen(true)
  }

  const save = async (ev) => {
    ev.preventDefault()
    if (!form.monthly_limit || Number(form.monthly_limit) <= 0) {
      toast.error('Enter a valid limit')
      return
    }
    setSaving(true)
    try {
      if (editing) {
        await budgetService.update(editing.id, {
          monthly_limit: Number(form.monthly_limit),
        })
        toast.success('Budget updated')
      } else {
        await budgetService.create({
          category: form.category,
          monthly_limit: Number(form.monthly_limit),
        })
        toast.success('Budget created')
      }
      setModalOpen(false)
      refetch()
    } catch (e) {
      toast.error(e.message)
    } finally {
      setSaving(false)
    }
  }

  const remove = async (b) => {
    if (!confirm(`Delete the ${b.category} budget?`)) return
    try {
      await budgetService.remove(b.id)
      toast.success('Budget deleted')
      refetch()
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

  return (
    <div>
      <PageHeader
        title="Budgets"
        subtitle="Set monthly limits per category"
        action={<Button onClick={openCreate}>+ Add Budget</Button>}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="This Month's Utilization">
          <BudgetProgress items={data.utilization} />
        </Card>

        <Card title="Your Budgets">
          {data.budgets.length ? (
            <div className="space-y-2">
              {data.budgets.map((b) => (
                <div
                  key={b.id}
                  className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2.5 dark:border-slate-800"
                >
                  <div>
                    <p className="font-medium text-slate-700 dark:text-slate-200">
                      {b.category}
                    </p>
                    <p className="text-xs text-slate-400">
                      {formatCurrency(b.monthly_limit)} / month
                    </p>
                  </div>
                  <div className="flex gap-3 text-sm">
                    <button
                      onClick={() => openEdit(b)}
                      className="text-brand-600 hover:underline"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => remove(b)}
                      className="text-rose-600 hover:underline"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="py-8 text-center text-sm text-slate-400">
              No budgets yet. Create one to start tracking limits.
            </p>
          )}
        </Card>
      </div>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Edit Budget' : 'Add Budget'}
      >
        <form onSubmit={save} className="space-y-4">
          <Select
            label="Category"
            value={form.category}
            disabled={!!editing}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
            options={CATEGORIES}
          />
          <Input
            label="Monthly limit"
            type="number"
            step="0.01"
            min="0"
            value={form.monthly_limit}
            onChange={(e) => setForm({ ...form, monthly_limit: e.target.value })}
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
