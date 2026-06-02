import api from './api'

export const budgetService = {
  list: () => api.get('/budgets').then((r) => r.data),
  utilization: () => api.get('/budgets/utilization').then((r) => r.data),
  create: (payload) => api.post('/budgets', payload).then((r) => r.data),
  update: (id, payload) => api.put(`/budgets/${id}`, payload).then((r) => r.data),
  remove: (id) => api.delete(`/budgets/${id}`).then((r) => r.data),
}
