import { createRouter, createWebHistory } from 'vue-router'
import SubscriptionList from '../views/SubscriptionList.vue'
import Calendar from '../views/Calendar.vue'
import Settings from '../views/Settings.vue'
import Analytics from '../views/Analytics.vue'

const routes = [
  {
    path: '/',
    name: 'SubscriptionList',
    component: SubscriptionList
  },
  {
    path: '/calendar',
    name: 'Calendar',
    component: Calendar
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router