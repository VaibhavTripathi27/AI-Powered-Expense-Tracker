import api from './api'

export const authService = {
  register: (payload) =>
    api.post('/auth/register', payload, { _skipAuthRedirect: true }).then((r) => r.data),
  login: (payload) =>
    api.post('/auth/login', payload, { _skipAuthRedirect: true }).then((r) => r.data),
  me: () => api.get('/auth/me').then((r) => r.data),
  logout: () => api.post('/auth/logout').then((r) => r.data),
}
