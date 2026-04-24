import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// ── 学生 ──
export const studentsApi = {
  list: () => api.get('/api/students'),
  get: (id) => api.get(`/api/students/${id}`),
  create: (data) => api.post('/api/students', data),
  update: (id, data) => api.put(`/api/students/${id}`, data),
  delete: (id) => api.delete(`/api/students/${id}`),
}

// ── 培训 ──
export const trainingsApi = {
  list: () => api.get('/api/trainings'),
  get: (id) => api.get(`/api/trainings/${id}`),
  create: (data) => api.post('/api/trainings', data),
  update: (id, data) => api.put(`/api/trainings/${id}`, data),
  delete: (id) => api.delete(`/api/trainings/${id}`),
}

// ── 记录 ──
export const recordsApi = {
  list: (params = {}) => api.get('/api/records', { params }),
  create: (data) => api.post('/api/records', data),
  delete: (id) => api.delete(`/api/records/${id}`),
}

// ── 仪表盘 ──
export const dashboardApi = {
  stats: () => api.get('/api/dashboard'),
  studentProgress: (id) => api.get(`/api/students/${id}/progress`),
  trainingStats: (id) => api.get(`/api/trainings/${id}/stats`),
  seedDemo: () => api.post('/api/demo-data'),
  clearAll: () => api.delete('/api/clear-data'),
}

export default api
