import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router'
import App from './App.vue'

// Import only the icons used in the project
import {
  List,
  Calendar,
  Setting,
  ArrowLeft,
  ArrowRight,
  Grid,
  Menu,
  Plus,
  MoreFilled,
  CreditCard,
  ChatDotRound,
  User,
  Check,
  Bell,
  Clock
} from '@element-plus/icons-vue'

const app = createApp(App)

app.use(ElementPlus)
app.use(router)

// Register only the icons we actually use
const icons = {
  List,
  Calendar,
  Setting,
  ArrowLeft,
  ArrowRight,
  Grid,
  Menu,
  Plus,
  MoreFilled,
  CreditCard,
  ChatDotRound,
  User,
  Check,
  Bell,
  Clock
}

// Register icons efficiently
for (const [key, component] of Object.entries(icons)) {
  app.component(key, component)
}

app.mount('#app')