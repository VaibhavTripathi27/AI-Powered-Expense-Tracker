import api from './api'

export const insightService = {
  get: () => api.get('/insights').then((r) => r.data),
}
