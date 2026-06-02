import api from './api'

export const alertService = {
  list: (params = {}) => api.get('/alerts', { params }).then((r) => r.data),
  markRead: (id) => api.patch(`/alerts/${id}/read`).then((r) => r.data),
  markAllRead: () => api.patch('/alerts/read-all').then((r) => r.data),
  remove: (id) => api.delete(`/alerts/${id}`).then((r) => r.data),
}
