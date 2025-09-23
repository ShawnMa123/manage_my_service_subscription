<template>
  <div class="subscription-list">
    <div class="header-section">
      <h2>订阅列表</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        添加订阅
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="24" v-if="loading">
        <el-skeleton :rows="5" animated />
      </el-col>
      <el-col :span="24" v-else-if="subscriptions.length === 0">
        <el-empty description="暂无订阅数据">
          <el-button type="primary" @click="showAddDialog = true">添加第一个订阅</el-button>
        </el-empty>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="8" :xl="6" v-for="subscription in subscriptions" :key="subscription.id">
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
          </div>
        </el-card>
      </el-col>
    </el-row>

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
import { ref, reactive, onMounted } from 'vue'
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
      loadSubscriptions,
      cancelForm,
      submitForm,
      handleCardAction,
      formatDate,
      getCountdownText,
      getCountdownClass,
      getCycleText,
      getCycleTagType
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
}

.header-section h2 {
  margin: 0;
  color: #303133;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式样式 */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .header-section h2 {
    text-align: center;
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
}
</style>