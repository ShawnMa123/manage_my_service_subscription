import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export const subscriptionApi = {
  // Get all subscriptions
  getAll: () => api.get('/subscriptions'),

  // Get subscription by ID
  getById: (id) => api.get(`/subscriptions/${id}`),

  // Create new subscription
  create: (data) => api.post('/subscriptions', data),

  // Update subscription
  update: (id, data) => api.put(`/subscriptions/${id}`, data),

  // Delete subscription
  delete: (id) => api.delete(`/subscriptions/${id}`)
}

export const settingsApi = {
  // Get all settings
  getAll: () => api.get('/settings'),

  // Get setting by key
  getByKey: (key) => api.get(`/settings/${key}`),

  // Update multiple settings
  updateMultiple: (settings) => api.post('/settings', settings),

  // Update single setting
  update: (key, data) => api.put(`/settings/${key}`, data)
}

export default api