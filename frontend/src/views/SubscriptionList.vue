<template>
  <div class="subscription-list">
    <div class="header-section">
      <h2>订阅列表</h2>
      <div class="header-controls">
        <!-- 视图切换控件 -->
        <div class="view-controls">
          <el-radio-group v-model="viewMode" size="small" @change="onViewModeChange">
            <el-radio-button label="card">
              <el-icon><Grid /></el-icon>
              卡片
            </el-radio-button>
            <el-radio-button label="list">
              <el-icon><List /></el-icon>
              列表
            </el-radio-button>
            <el-radio-button label="table">
              <el-icon><Menu /></el-icon>
              表格
            </el-radio-button>
          </el-radio-group>
        </div>

        <!-- 排序控件 -->
        <div class="sort-controls">
          <el-select v-model="sortBy" placeholder="排序方式" size="small" style="width: 120px">
            <el-option label="名称" value="name" />
            <el-option label="价格" value="price" />
            <el-option label="到期日" value="next_due_date" />
            <el-option label="创建时间" value="created_at" />
          </el-select>
          <el-button
            size="small"
            @click="toggleSortOrder"
            :icon="sortOrder === 'asc' ? 'sort-up' : 'sort-down'"
          >
            {{ sortOrder === 'asc' ? '升序' : '降序' }}
          </el-button>
        </div>

        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加订阅
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 空状态 -->
    <div v-else-if="sortedSubscriptions.length === 0" class="empty-container">
      <el-empty description="暂无订阅数据">
        <el-button type="primary" @click="showAddDialog = true">添加第一个订阅</el-button>
      </el-empty>
    </div>

    <!-- 卡片视图 -->
    <el-row v-else-if="viewMode === 'card'" :gutter="20">
      <el-col :xs="24" :sm="24" :md="12" :lg="8" :xl="6" v-for="subscription in sortedSubscriptions" :key="subscription.id">
        <el-card class="subscription-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="subscription-name">{{ subscription.name }}</span>
              <el-dropdown @command="handleCardAction">
                <el-icon class="action-icon"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="{ action: 'edit', subscription }">编辑</el-dropdown-item>
                    <el-dropdown-item :command="{ action: 'delete', subscription }">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <div class="card-content">
            <div class="price-section">
              <span class="price">{{ subscription.price }}</span>
              <span class="currency">{{ subscription.currency }}</span>
            </div>
            <div class="cycle-section">
              <el-tag :type="getCycleTagType(subscription.cycle)">
                {{ getCycleText(subscription.cycle) }}
              </el-tag>
            </div>
            <div class="due-date-section">
              <div class="due-date">下次续费: {{ formatDate(subscription.next_due_date) }}</div>
              <div class="countdown" :class="getCountdownClass(subscription.next_due_date)">
                {{ getCountdownText(subscription.next_due_date) }}
              </div>
            </div>
            <div class="notes-section" v-if="subscription.notes">
              <el-text class="notes" type="info" size="small">{{ subscription.notes }}</el-text>
            </div>
            <div class="actions-section">
              <el-button
                type="success"
                size="small"
                @click="renewSubscription(subscription)"
                :loading="renewingId === subscription.id"
                :disabled="!isNearDue(subscription.next_due_date)"
              >
                <el-icon><CreditCard /></el-icon>
                续费
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 列表视图 -->
    <div v-else-if="viewMode === 'list'" class="list-view">
      <div class="list-item" v-for="subscription in sortedSubscriptions" :key="subscription.id">
        <div class="list-item-content">
          <div class="list-item-main">
            <div class="list-item-header">
              <h3 class="list-item-title">{{ subscription.name }}</h3>
              <div class="list-item-actions">
                <el-button
                  type="success"
                  size="small"
                  @click="renewSubscription(subscription)"
                  :loading="renewingId === subscription.id"
                  :disabled="!isNearDue(subscription.next_due_date)"
                >
                  <el-icon><CreditCard /></el-icon>
                  续费
                </el-button>
                <el-dropdown @command="handleCardAction">
                  <el-button size="small" type="text">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{ action: 'edit', subscription }">编辑</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'delete', subscription }">删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            <div class="list-item-info">
              <div class="list-item-price">
                <span class="price">{{ subscription.price }}</span>
                <span class="currency">{{ subscription.currency }}</span>
                <el-tag :type="getCycleTagType(subscription.cycle)" size="small">
                  {{ getCycleText(subscription.cycle) }}
                </el-tag>
              </div>
              <div class="list-item-due">
                <span class="due-label">下次续费:</span>
                <span class="due-date">{{ formatDate(subscription.next_due_date) }}</span>
                <span class="countdown" :class="getCountdownClass(subscription.next_due_date)">
                  {{ getCountdownText(subscription.next_due_date) }}
                </span>
              </div>
              <div class="list-item-notes" v-if="subscription.notes">
                <el-text type="info" size="small">{{ subscription.notes }}</el-text>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 表格视图 -->
    <el-table v-else-if="viewMode === 'table'" :data="sortedSubscriptions" class="table-view" stripe>
      <el-table-column prop="name" label="订阅名称" min-width="150">
        <template #default="{ row }">
          <strong>{{ row.name }}</strong>
        </template>
      </el-table-column>

      <el-table-column label="价格" min-width="120" sortable="custom" prop="price">
        <template #default="{ row }">
          <span class="table-price">{{ row.price }} {{ row.currency }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="cycle" label="周期" width="100">
        <template #default="{ row }">
          <el-tag :type="getCycleTagType(row.cycle)" size="small">
            {{ getCycleText(row.cycle) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="next_due_date" label="到期日" min-width="140" sortable="custom">
        <template #default="{ row }">
          <div>
            <div>{{ formatDate(row.next_due_date) }}</div>
            <div class="countdown table-countdown" :class="getCountdownClass(row.next_due_date)">
              {{ getCountdownText(row.next_due_date) }}
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="notes" label="备注" min-width="150">
        <template #default="{ row }">
          <el-text v-if="row.notes" type="info" size="small">{{ row.notes }}</el-text>
          <span v-else class="text-placeholder">-</span>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button
            type="success"
            size="small"
            @click="renewSubscription(row)"
            :loading="renewingId === row.id"
            :disabled="!isNearDue(row.next_due_date)"
          >
            <el-icon><CreditCard /></el-icon>
            续费
          </el-button>
          <el-dropdown @command="handleCardAction">
            <el-button size="small" type="text">
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :command="{ action: 'edit', subscription: row }">编辑</el-dropdown-item>
                <el-dropdown-item :command="{ action: 'delete', subscription: row }">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <!-- Add/Edit Dialog -->
    <el-dialog
      :title="editingSubscription ? '编辑订阅' : '添加订阅'"
      v-model="showAddDialog"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="订阅名称" prop="name">
          <el-input v-model="form.name" placeholder="如: Netflix Premium" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="form.price" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="货币" prop="currency">
          <el-select v-model="form.currency" placeholder="选择货币">
            <el-option label="人民币 (CNY)" value="CNY" />
            <el-option label="美元 (USD)" value="USD" />
            <el-option label="欧元 (EUR)" value="EUR" />
          </el-select>
        </el-form-item>
        <el-form-item label="续费周期" prop="cycle">
          <el-select v-model="form.cycle" placeholder="选择续费周期">
            <el-option label="月度" value="monthly" />
            <el-option label="季度" value="quarterly" />
            <el-option label="年度" value="yearly" />
          </el-select>
        </el-form-item>
        <el-form-item label="下次续费" prop="next_due_date">
          <el-date-picker
            v-model="form.next_due_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="2"
            placeholder="可选"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelForm">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ editingSubscription ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { subscriptionApi } from '../api'
import dayjs from 'dayjs'

export default {
  name: 'SubscriptionList',
  setup() {
    const subscriptions = ref([])
    const loading = ref(false)
    const showAddDialog = ref(false)
    const submitting = ref(false)
    const editingSubscription = ref(null)
    const formRef = ref()
    const renewingId = ref(null)
    const viewMode = ref('card')
    const sortBy = ref('next_due_date')
    const sortOrder = ref('asc')

    const form = reactive({
      name: '',
      price: 0,
      currency: 'CNY',
      cycle: 'monthly',
      next_due_date: '',
      notes: ''
    })

    const rules = {
      name: [{ required: true, message: '请输入订阅名称', trigger: 'blur' }],
      price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
      currency: [{ required: true, message: '请选择货币', trigger: 'change' }],
      cycle: [{ required: true, message: '请选择续费周期', trigger: 'change' }],
      next_due_date: [{ required: true, message: '请选择下次续费日期', trigger: 'change' }]
    }

    // 排序后的订阅列表
    const sortedSubscriptions = computed(() => {
      const sorted = [...subscriptions.value].sort((a, b) => {
        let aValue = a[sortBy.value]
        let bValue = b[sortBy.value]

        // 特殊处理不同类型的数据
        if (sortBy.value === 'price') {
          aValue = parseFloat(aValue) || 0
          bValue = parseFloat(bValue) || 0
        } else if (sortBy.value === 'next_due_date' || sortBy.value === 'created_at') {
          aValue = new Date(aValue)
          bValue = new Date(bValue)
        } else if (typeof aValue === 'string') {
          aValue = aValue.toLowerCase()
          bValue = bValue.toLowerCase()
        }

        if (sortOrder.value === 'asc') {
          return aValue > bValue ? 1 : aValue < bValue ? -1 : 0
        } else {
          return aValue < bValue ? 1 : aValue > bValue ? -1 : 0
        }
      })
      return sorted
    })

    const loadSubscriptions = async () => {
      loading.value = true
      try {
        const response = await subscriptionApi.getAll()
        subscriptions.value = response.data
      } catch (error) {
        ElMessage.error('加载订阅列表失败')
        console.error(error)
      }
      loading.value = false
    }

    const resetForm = () => {
      Object.assign(form, {
        name: '',
        price: 0,
        currency: 'CNY',
        cycle: 'monthly',
        next_due_date: '',
        notes: ''
      })
      editingSubscription.value = null
    }

    const cancelForm = () => {
      showAddDialog.value = false
      resetForm()
      formRef.value?.resetFields()
    }

    const submitForm = async () => {
      if (!formRef.value) return

      const isValid = await formRef.value.validate().catch(() => false)
      if (!isValid) return

      submitting.value = true
      try {
        if (editingSubscription.value) {
          await subscriptionApi.update(editingSubscription.value.id, form)
          ElMessage.success('订阅更新成功')
        } else {
          await subscriptionApi.create(form)
          ElMessage.success('订阅添加成功')
        }
        showAddDialog.value = false
        resetForm()
        loadSubscriptions()
      } catch (error) {
        ElMessage.error(editingSubscription.value ? '更新失败' : '添加失败')
        console.error(error)
      }
      submitting.value = false
    }

    const handleCardAction = async ({ action, subscription }) => {
      if (action === 'edit') {
        editingSubscription.value = subscription
        Object.assign(form, subscription)
        showAddDialog.value = true
      } else if (action === 'delete') {
        try {
          await ElMessageBox.confirm('确定要删除这个订阅吗？', '确认删除', {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning'
          })
          await subscriptionApi.delete(subscription.id)
          ElMessage.success('删除成功')
          loadSubscriptions()
        } catch (error) {
          if (error !== 'cancel') {
            ElMessage.error('删除失败')
            console.error(error)
          }
        }
      }
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

    const getCycleTagType = (cycle) => {
      const typeMap = {
        monthly: 'primary',
        quarterly: 'warning',
        yearly: 'success'
      }
      return typeMap[cycle] || ''
    }

    const isNearDue = (dateStr) => {
      const diff = dayjs(dateStr).diff(dayjs(), 'day')
      return diff <= 3 && diff >= 0  // 3天内且未过期
    }

    const renewSubscription = async (subscription) => {
      try {
        await ElMessageBox.confirm(
          `确定要续费订阅 "${subscription.name}" 吗？续费后将自动延长一个付费周期。`,
          '确认续费',
          {
            confirmButtonText: '确认续费',
            cancelButtonText: '取消',
            type: 'info'
          }
        )

        renewingId.value = subscription.id
        await subscriptionApi.renew(subscription.id)
        ElMessage.success(`${subscription.name} 续费成功！`)
        loadSubscriptions()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('续费失败')
          console.error(error)
        }
      } finally {
        renewingId.value = null
      }
    }

    onMounted(() => {
      loadSubscriptions()
    })

    return {
      subscriptions,
      loading,
      showAddDialog,
      submitting,
      editingSubscription,
      formRef,
      form,
      rules,
      renewingId,
      loadSubscriptions,
      cancelForm,
      submitForm,
      handleCardAction,
      renewSubscription,
      isNearDue,
      formatDate,
      getCountdownText,
      getCountdownClass,
      getCycleText,
      getCycleTagType,
      viewMode,
      sortBy,
      sortOrder,
      sortedSubscriptions,
      onViewModeChange: () => {},
      toggleSortOrder: () => {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
      }
    }
  }
}
</script>

<style scoped>
.subscription-list {
  padding: 20px 0;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.header-section h2 {
  margin: 0;
  color: #303133;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.view-controls {
  display: flex;
  align-items: center;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.subscription-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subscription-name {
  font-weight: 500;
  font-size: 16px;
}

.action-icon {
  cursor: pointer;
  color: #909399;
}

.action-icon:hover {
  color: #409eff;
}

.card-content {
  padding: 0;
}

.price-section {
  margin-bottom: 12px;
}

.price {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.currency {
  font-size: 14px;
  color: #909399;
  margin-left: 4px;
}

.cycle-section {
  margin-bottom: 12px;
}

.due-date-section {
  margin-bottom: 12px;
}

.due-date {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.countdown {
  font-size: 12px;
  font-weight: 500;
}

.countdown.normal {
  color: #67c23a;
}

.countdown.warning {
  color: #e6a23c;
}

.countdown.urgent {
  color: #f56c6c;
}

.countdown.overdue {
  color: #f56c6c;
  font-weight: 600;
}

.notes-section {
  margin-top: 12px;
}

.notes {
  font-size: 12px;
}

.actions-section {
  margin-top: 15px;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 列表视图样式 */
.list-view {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-item {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s;
}

.list-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.list-item-content {
  width: 100%;
}

.list-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.list-item-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.list-item-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.list-item-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  align-items: start;
}

.list-item-price {
  display: flex;
  align-items: center;
  gap: 8px;
}

.list-item-price .price {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.list-item-price .currency {
  font-size: 14px;
  color: #909399;
}

.list-item-due {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.due-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.list-item-notes {
  grid-column: 1 / -1;
  margin-top: 8px;
}

/* 表格视图样式 */
.table-view {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.table-price {
  font-weight: 500;
  color: #303133;
}

.table-countdown {
  font-size: 11px;
  margin-top: 2px;
}

.text-placeholder {
  color: #c0c4cc;
  font-style: italic;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: stretch;
  }

  .header-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .view-controls,
  .sort-controls {
    justify-content: center;
  }

  .list-item-info {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .list-item-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .list-item-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .subscription-list {
    padding: 10px 0;
  }

  .subscription-card {
    margin-bottom: 15px;
  }

  .price {
    font-size: 20px;
  }

  .header-controls {
    gap: 10px;
  }

  .view-controls .el-radio-group {
    width: 100%;
  }

  .list-item {
    padding: 15px;
  }

  .list-item-title {
    font-size: 16px;
  }

  .list-item-price .price {
    font-size: 18px;
  }
}
</style>