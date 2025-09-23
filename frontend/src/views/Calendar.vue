<template>
  <div class="calendar-view">
    <div class="header-section">
      <h2>日历视图</h2>
      <div class="calendar-controls">
        <el-button-group>
          <el-button @click="previousMonth">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <el-button @click="nextMonth">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </el-button-group>
        <el-button @click="goToday" type="primary" plain>今天</el-button>
      </div>
    </div>

    <div class="calendar-container">
      <el-calendar v-model="currentDate" ref="calendarRef">
        <template #header="{ date }">
          <div class="calendar-header">
            <span class="month-year">{{ formatMonthYear(date) }}</span>
          </div>
        </template>
        <template #date-cell="{ data }">
          <div class="calendar-cell" :class="getCellClass(data.day)">
            <div class="date-number">{{ data.day.split('-').pop() }}</div>
            <div class="subscription-events">
              <div
                v-for="subscription in getSubscriptionsForDate(data.day)"
                :key="subscription.id"
                class="subscription-event"
                :class="getEventClass(subscription)"
                @click="showSubscriptionDetail(subscription)"
              >
                <div class="event-name">{{ subscription.name }}</div>
                <div class="event-price">{{ subscription.price }} {{ subscription.currency }}</div>
              </div>
            </div>
          </div>
        </template>
      </el-calendar>
    </div>

    <!-- Subscription Detail Dialog -->
    <el-dialog
      title="订阅详情"
      v-model="showDetailDialog"
      width="400px"
    >
      <div v-if="selectedSubscription" class="subscription-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="订阅名称">
            {{ selectedSubscription.name }}
          </el-descriptions-item>
          <el-descriptions-item label="价格">
            {{ selectedSubscription.price }} {{ selectedSubscription.currency }}
          </el-descriptions-item>
          <el-descriptions-item label="续费周期">
            {{ getCycleText(selectedSubscription.cycle) }}
          </el-descriptions-item>
          <el-descriptions-item label="下次续费">
            {{ formatDate(selectedSubscription.next_due_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="倒计时">
            <span :class="getCountdownClass(selectedSubscription.next_due_date)">
              {{ getCountdownText(selectedSubscription.next_due_date) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedSubscription.notes" label="备注">
            {{ selectedSubscription.notes }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- Legend -->
    <div class="legend">
      <h3>图例</h3>
      <div class="legend-items">
        <div class="legend-item">
          <div class="legend-color urgent"></div>
          <span>紧急 (1-3天)</span>
        </div>
        <div class="legend-item">
          <div class="legend-color warning"></div>
          <span>提醒 (4-7天)</span>
        </div>
        <div class="legend-item">
          <div class="legend-color normal"></div>
          <span>正常 (7天以上)</span>
        </div>
        <div class="legend-item">
          <div class="legend-color overdue"></div>
          <span>已过期</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { subscriptionApi } from '../api'
import dayjs from 'dayjs'

export default {
  name: 'Calendar',
  setup() {
    const subscriptions = ref([])
    const currentDate = ref(new Date())
    const showDetailDialog = ref(false)
    const selectedSubscription = ref(null)
    const calendarRef = ref()

    const loadSubscriptions = async () => {
      try {
        const response = await subscriptionApi.getAll()
        subscriptions.value = response.data
      } catch (error) {
        ElMessage.error('加载订阅列表失败')
        console.error(error)
      }
    }

    const getSubscriptionsForDate = (date) => {
      return subscriptions.value.filter(subscription =>
        subscription.next_due_date === date
      )
    }

    const getCellClass = (date) => {
      const today = dayjs().format('YYYY-MM-DD')
      const subscriptionsForDate = getSubscriptionsForDate(date)

      let classes = []

      if (date === today) {
        classes.push('today')
      }

      if (subscriptionsForDate.length > 0) {
        classes.push('has-events')
      }

      return classes
    }

    const getEventClass = (subscription) => {
      const diff = dayjs(subscription.next_due_date).diff(dayjs(), 'day')
      if (diff < 0) return 'overdue'
      if (diff <= 3) return 'urgent'
      if (diff <= 7) return 'warning'
      return 'normal'
    }

    const showSubscriptionDetail = (subscription) => {
      selectedSubscription.value = subscription
      showDetailDialog.value = true
    }

    const formatMonthYear = (date) => {
      return dayjs(date).format('YYYY年MM月')
    }

    const formatDate = (dateStr) => {
      return dayjs(dateStr).format('YYYY年MM月DD日')
    }

    const getCountdownText = (dateStr) => {
      const diff = dayjs(dateStr).diff(dayjs(), 'day')
      if (diff < 0) {
        return `已过期 ${Math.abs(diff)} 天`
      } else if (diff === 0) {
        return '今天到期'
      } else {
        return `还有 ${diff} 天`
      }
    }

    const getCountdownClass = (dateStr) => {
      const diff = dayjs(dateStr).diff(dayjs(), 'day')
      if (diff < 0) return 'overdue'
      if (diff <= 3) return 'urgent'
      if (diff <= 7) return 'warning'
      return 'normal'
    }

    const getCycleText = (cycle) => {
      const cycleMap = {
        monthly: '月度',
        quarterly: '季度',
        yearly: '年度'
      }
      return cycleMap[cycle] || cycle
    }

    const previousMonth = () => {
      currentDate.value = dayjs(currentDate.value).subtract(1, 'month').toDate()
    }

    const nextMonth = () => {
      currentDate.value = dayjs(currentDate.value).add(1, 'month').toDate()
    }

    const goToday = () => {
      currentDate.value = new Date()
    }

    onMounted(() => {
      loadSubscriptions()
    })

    return {
      subscriptions,
      currentDate,
      showDetailDialog,
      selectedSubscription,
      calendarRef,
      getSubscriptionsForDate,
      getCellClass,
      getEventClass,
      showSubscriptionDetail,
      formatMonthYear,
      formatDate,
      getCountdownText,
      getCountdownClass,
      getCycleText,
      previousMonth,
      nextMonth,
      goToday
    }
  }
}
</script>

<style scoped>
.calendar-view {
  padding: 20px 0;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-section h2 {
  margin: 0;
  color: #303133;
}

.calendar-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.calendar-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.calendar-header {
  text-align: center;
  padding: 10px 0;
}

.month-year {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.calendar-cell {
  min-height: 80px;
  padding: 4px;
  position: relative;
}

.calendar-cell.today {
  background-color: #f0f9ff;
}

.calendar-cell.has-events {
  background-color: #fafafa;
}

.date-number {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  color: #303133;
}

.subscription-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.subscription-event {
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid;
}

.subscription-event:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.subscription-event.normal {
  background-color: #f0f9ff;
  border-left-color: #409eff;
  color: #409eff;
}

.subscription-event.warning {
  background-color: #fdf6ec;
  border-left-color: #e6a23c;
  color: #e6a23c;
}

.subscription-event.urgent {
  background-color: #fef0f0;
  border-left-color: #f56c6c;
  color: #f56c6c;
}

.subscription-event.overdue {
  background-color: #fef0f0;
  border-left-color: #f56c6c;
  color: #f56c6c;
  font-weight: 600;
}

.event-name {
  font-weight: 500;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-price {
  font-size: 10px;
  opacity: 0.8;
}

.subscription-detail {
  padding: 10px 0;
}

.legend {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.legend h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.legend-items {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border-left: 3px solid;
}

.legend-color.normal {
  background-color: #f0f9ff;
  border-left-color: #409eff;
}

.legend-color.warning {
  background-color: #fdf6ec;
  border-left-color: #e6a23c;
}

.legend-color.urgent {
  background-color: #fef0f0;
  border-left-color: #f56c6c;
}

.legend-color.overdue {
  background-color: #fef0f0;
  border-left-color: #f56c6c;
}

.urgent {
  color: #f56c6c;
  font-weight: 500;
}

.warning {
  color: #e6a23c;
  font-weight: 500;
}

.normal {
  color: #67c23a;
  font-weight: 500;
}

.overdue {
  color: #f56c6c;
  font-weight: 600;
}

:deep(.el-calendar-table .el-calendar-day) {
  padding: 0;
}

:deep(.el-calendar__header) {
  display: none;
}
</style>