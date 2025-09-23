import { createRouter, createWebHistory } from 'vue-router'
import SubscriptionList from '../views/SubscriptionList.vue'
import Calendar from '../views/Calendar.vue'
import Settings from '../views/Settings.vue'

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