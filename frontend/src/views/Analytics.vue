<template>
  <div class="analytics-container">
    <div class="page-header">
      <h1>📊 趋势分析</h1>
      <p>深入了解您的订阅服务使用情况和支出趋势</p>
    </div>

    <el-skeleton v-if="loading" :rows="10" animated />

    <div v-else>
      <!-- 总览卡片 -->
      <el-row :gutter="20" class="overview-cards">
        <el-col :xs="12" :sm="6" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ analyticsData.subscription_analytics?.total_subscriptions || 0 }}</div>
              <div class="stat-label">总订阅数</div>
              <div class="stat-icon">📋</div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">¥{{ formatCurrency(analyticsData.subscription_analytics?.total_monthly_cost || 0) }}</div>
              <div class="stat-label">月度支出</div>
              <div class="stat-icon">💰</div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">¥{{ formatCurrency(analyticsData.subscription_analytics?.total_yearly_cost || 0) }}</div>
              <div class="stat-label">年度支出</div>
              <div class="stat-icon">📈</div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ analyticsData.subscription_analytics?.upcoming_renewals?.length || 0 }}</div>
              <div class="stat-label">即将到期</div>
              <div class="stat-icon">⏰</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" class="charts-row">
        <!-- 月度支出趋势 -->
        <el-col :xs="24" :md="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>📊 月度支出趋势</span>
              </div>
            </template>
            <div class="chart-container">
              <Line
                v-if="monthlySpendingChart.data"
                :data="monthlySpendingChart.data"
                :options="monthlySpendingChart.options"
              />
            </div>
          </el-card>
        </el-col>

        <!-- 订阅周期分布 -->
        <el-col :xs="24" :md="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>🍕 订阅周期分布</span>
              </div>
            </template>
            <div class="chart-container">
              <Doughnut
                v-if="cycleDistributionChart.data"
                :data="cycleDistributionChart.data"
                :options="cycleDistributionChart.options"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="charts-row">
        <!-- 订阅创建时间线 -->
        <el-col :xs="24" :md="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>📅 订阅创建时间线</span>
              </div>
            </template>
            <div class="chart-container">
              <Bar
                v-if="creationTimelineChart.data"
                :data="creationTimelineChart.data"
                :options="creationTimelineChart.options"
              />
            </div>
          </el-card>
        </el-col>

        <!-- 续费预测 -->
        <el-col :xs="24" :md="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>🔮 续费预测</span>
              </div>
            </template>
            <div class="chart-container">
              <Line
                v-if="renewalTimelineChart.data"
                :data="renewalTimelineChart.data"
                :options="renewalTimelineChart.options"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 价格区间分析 -->
      <el-row :gutter="20" class="charts-row">
        <el-col :xs="24">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>💸 价格区间分析</span>
              </div>
            </template>
            <div class="chart-container">
              <Bar
                v-if="priceRangeChart.data"
                :data="priceRangeChart.data"
                :options="priceRangeChart.options"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 即将到期的订阅 -->
      <el-row :gutter="20" v-if="analyticsData.subscription_analytics?.upcoming_renewals?.length > 0">
        <el-col :span="24">
          <el-card class="upcoming-renewals">
            <template #header>
              <div class="card-header">
                <span>⏰ 即将到期的订阅</span>
              </div>
            </template>
            <el-table :data="analyticsData.subscription_analytics.upcoming_renewals" stripe>
              <el-table-column prop="name" label="订阅名称" />
              <el-table-column prop="price" label="价格" :formatter="priceFormatter" />
              <el-table-column prop="cycle" label="周期">
                <template #default="scope">
                  <el-tag :type="getCycleTagType(scope.row.cycle)">
                    {{ getCycleText(scope.row.cycle) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="next_due_date" label="到期日期">
                <template #default="scope">
                  <span :class="{'overdue': isOverdue(scope.row.next_due_date)}">
                    {{ formatDate(scope.row.next_due_date) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="剩余天数">
                <template #default="scope">
                  <el-tag :type="getDaysRemainingType(scope.row.next_due_date)">
                    {{ getDaysRemaining(scope.row.next_due_date) }}天
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { Line, Bar, Doughnut } from 'vue-chartjs'
import { analyticsApi } from '../api'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

const loading = ref(true)
const analyticsData = ref({})

// 图表数据
const monthlySpendingChart = reactive({
  data: null,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '¥' + value.toFixed(2)
          }
        }
      }
    }
  }
})

const cycleDistributionChart = reactive({
  data: null,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  }
})

const creationTimelineChart = reactive({
  data: null,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
})

const renewalTimelineChart = reactive({
  data: null,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '¥' + value.toFixed(2)
          }
        }
      }
    }
  }
})

const priceRangeChart = reactive({
  data: null,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
})

// 辅助函数
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const formatDate = (dateStr) => {
  return dayjs(dateStr).format('YYYY-MM-DD')
}

const getCycleText = (cycle) => {
  const cycleMap = {
    'monthly': '月度',
    'quarterly': '季度',
    'yearly': '年度'
  }
  return cycleMap[cycle] || cycle
}

const getCycleTagType = (cycle) => {
  const typeMap = {
    'monthly': 'success',
    'quarterly': 'warning',
    'yearly': 'danger'
  }
  return typeMap[cycle] || ''
}

const isOverdue = (dateStr) => {
  return dayjs(dateStr).isBefore(dayjs())
}

const getDaysRemaining = (dateStr) => {
  return dayjs(dateStr).diff(dayjs(), 'day')
}

const getDaysRemainingType = (dateStr) => {
  const days = getDaysRemaining(dateStr)
  if (days < 0) return 'danger'
  if (days <= 7) return 'warning'
  return 'success'
}

const priceFormatter = (row, column, cellValue) => {
  return '¥' + formatCurrency(cellValue)
}

// 准备图表数据
const prepareChartData = () => {
  if (!analyticsData.value.price_trend) return

  // 月度支出趋势图
  const monthlyData = analyticsData.value.price_trend.monthly_spending || []
  monthlySpendingChart.data = {
    labels: monthlyData.map(item => item.month),
    datasets: [
      {
        label: '月度支出',
        data: monthlyData.map(item => item.total_amount),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4
      }
    ]
  }

  // 订阅周期分布
  const cycleData = analyticsData.value.subscription_analytics.cycle_breakdown || []
  cycleDistributionChart.data = {
    labels: cycleData.map(item => getCycleText(item.cycle)),
    datasets: [
      {
        data: cycleData.map(item => item.count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)'
        ]
      }
    ]
  }

  // 创建时间线
  const creationData = analyticsData.value.creation_timeline || []
  creationTimelineChart.data = {
    labels: creationData.map(item => item.date),
    datasets: [
      {
        label: '新增订阅',
        data: creationData.map(item => item.count),
        backgroundColor: 'rgba(153, 102, 255, 0.8)'
      }
    ]
  }

  // 续费预测
  const renewalData = analyticsData.value.renewal_timeline || []
  renewalTimelineChart.data = {
    labels: renewalData.map(item => item.date),
    datasets: [
      {
        label: '预测续费金额',
        data: renewalData.map(item => item.amount),
        borderColor: 'rgb(255, 159, 64)',
        backgroundColor: 'rgba(255, 159, 64, 0.2)',
        tension: 0.4
      }
    ]
  }

  // 价格区间分析
  const priceRanges = analyticsData.value.subscription_analytics.price_ranges || {}
  priceRangeChart.data = {
    labels: Object.keys(priceRanges).map(range => range + '元'),
    datasets: [
      {
        label: '订阅数量',
        data: Object.values(priceRanges),
        backgroundColor: 'rgba(75, 192, 192, 0.8)'
      }
    ]
  }
}

// 加载数据
const loadAnalyticsData = async () => {
  try {
    loading.value = true
    const response = await analyticsApi.getComprehensive()
    analyticsData.value = response.data
    prepareChartData()
  } catch (error) {
    console.error('Failed to load analytics data:', error)
    ElMessage.error('加载趋势分析数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnalyticsData()
})
</script>

<style scoped>
.analytics-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h1 {
  font-size: 2.5rem;
  margin: 0 0 10px 0;
  color: #303133;
}

.page-header p {
  color: #909399;
  font-size: 1.1rem;
  margin: 0;
}

.overview-cards {
  margin-bottom: 30px;
}

.stat-card {
  height: 120px;
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  position: relative;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  color: #909399;
  font-size: 0.9rem;
}

.stat-icon {
  position: absolute;
  top: 10px;
  right: 15px;
  font-size: 1.5rem;
  opacity: 0.6;
}

.charts-row {
  margin-bottom: 30px;
}

.chart-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.chart-container {
  height: 300px;
  position: relative;
}

.upcoming-renewals {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.overdue {
  color: #F56C6C;
  font-weight: bold;
}

@media (max-width: 768px) {
  .analytics-container {
    padding: 10px;
  }

  .page-header h1 {
    font-size: 2rem;
  }

  .chart-container {
    height: 250px;
  }

  .stat-value {
    font-size: 1.5rem;
  }
}
</style>