import api from './api'

export const analyticsService = {
  dashboard: () => api.get('/analytics/dashboard').then((r) => r.data),
  healthScore: () => api.get('/analytics/health-score').then((r) => r.data),
}
