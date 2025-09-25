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
  delete: (id) => api.delete(`/subscriptions/${id}`),

  // Renew subscription
  renew: (id) => api.post(`/subscriptions/${id}/renew`)
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

export const telegramApi = {
  // Test Telegram notification
  test: () => api.post('/telegram/test')
}

export const analyticsApi = {
  // Get comprehensive analytics data
  getComprehensive: () => api.get('/analytics/comprehensive'),

  // Get subscription analytics
  getSubscriptionAnalytics: () => api.get('/analytics/subscription'),

  // Get price trend data
  getPriceTrend: () => api.get('/analytics/price-trend'),

  // Get creation timeline
  getCreationTimeline: () => api.get('/analytics/timeline/creation'),

  // Get renewal timeline
  getRenewalTimeline: () => api.get('/analytics/timeline/renewal')
}

export default api