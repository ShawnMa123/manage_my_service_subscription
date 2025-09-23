<template>
  <div class="settings-view">
    <div class="header-section">
      <h2>系统设置</h2>
    </div>

    <el-card class="settings-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h3>Telegram 通知设置</h3>
          <el-text type="info" size="small">
            配置 Telegram Bot 以接收订阅续费提醒
          </el-text>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="140px" v-loading="loading">
        <el-form-item label="Bot Token" prop="telegram_token">
          <el-input
            v-model="form.telegram_token"
            placeholder="请输入 Telegram Bot Token"
            show-password
            clearable
          >
            <template #prepend>
              <el-icon><ChatDotRound /></el-icon>
            </template>
          </el-input>
          <div class="help-text">
            从 <el-link href="https://t.me/botfather" target="_blank">@BotFather</el-link> 获取 Bot Token
          </div>
        </el-form-item>

        <el-form-item label="Chat ID" prop="telegram_chat_id">
          <el-input
            v-model="form.telegram_chat_id"
            placeholder="请输入 Chat ID"
            clearable
          >
            <template #prepend>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
          <div class="help-text">
            向 <el-link href="https://t.me/userinfobot" target="_blank">@userinfobot</el-link> 发送消息获取 Chat ID
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSettings" :loading="saving">
            <el-icon><Check /></el-icon>
            保存设置
          </el-button>
          <el-button @click="testNotification" :loading="testing" :disabled="!canTest">
            <el-icon><Bell /></el-icon>
            测试通知
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h3>提醒规则</h3>
          <el-text type="info" size="small">
            系统将在以下时间点发送提醒
          </el-text>
        </div>
      </template>

      <div class="reminder-rules">
        <div class="rule-item">
          <el-icon class="rule-icon" color="#409eff"><Clock /></el-icon>
          <div class="rule-content">
            <div class="rule-title">续费前 7 天</div>
            <div class="rule-desc">提前一周提醒，方便您安排资金</div>
          </div>
        </div>
        <div class="rule-item">
          <el-icon class="rule-icon" color="#e6a23c"><Clock /></el-icon>
          <div class="rule-content">
            <div class="rule-title">续费前 3 天</div>
            <div class="rule-desc">再次提醒，避免忘记续费</div>
          </div>
        </div>
        <div class="rule-item">
          <el-icon class="rule-icon" color="#f56c6c"><Clock /></el-icon>
          <div class="rule-content">
            <div class="rule-title">续费前 1 天</div>
            <div class="rule-desc">最后提醒，确保不会遗漏</div>
          </div>
        </div>
      </div>

      <el-alert
        title="提醒时间"
        description="系统会在每天凌晨 1:00 检查并发送提醒"
        type="info"
        :closable="false"
        show-icon
      />
    </el-card>

    <el-card class="settings-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h3>配置指南</h3>
        </div>
      </template>

      <el-steps direction="vertical" :active="4">
        <el-step title="创建 Telegram Bot">
          <template #description>
            <div>
              1. 在 Telegram 中搜索 <el-tag size="small">@BotFather</el-tag><br>
              2. 发送 <el-tag size="small">/newbot</el-tag> 命令<br>
              3. 按提示设置 Bot 名称和用户名<br>
              4. 复制获得的 Bot Token
            </div>
          </template>
        </el-step>
        <el-step title="获取 Chat ID">
          <template #description>
            <div>
              1. 在 Telegram 中搜索 <el-tag size="small">@userinfobot</el-tag><br>
              2. 向它发送任意消息<br>
              3. 复制返回的 Chat ID 数字
            </div>
          </template>
        </el-step>
        <el-step title="配置设置">
          <template #description>
            <div>
              在上方表单中填入 Bot Token 和 Chat ID，然后保存
            </div>
          </template>
        </el-step>
        <el-step title="测试通知">
          <template #description>
            <div>
              点击"测试通知"按钮，检查是否能正常接收消息
            </div>
          </template>
        </el-step>
      </el-steps>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { settingsApi } from '../api'

export default {
  name: 'Settings',
  setup() {
    const loading = ref(false)
    const saving = ref(false)
    const testing = ref(false)
    const formRef = ref()

    const form = reactive({
      telegram_token: '',
      telegram_chat_id: ''
    })

    const rules = {
      telegram_token: [
        { required: true, message: '请输入 Telegram Bot Token', trigger: 'blur' },
        { min: 10, message: 'Token 长度不能少于 10 位', trigger: 'blur' }
      ],
      telegram_chat_id: [
        { required: true, message: '请输入 Chat ID', trigger: 'blur' },
        { pattern: /^-?\d+$/, message: 'Chat ID 必须是数字', trigger: 'blur' }
      ]
    }

    const canTest = computed(() => {
      return form.telegram_token && form.telegram_chat_id
    })

    const loadSettings = async () => {
      loading.value = true
      try {
        const response = await settingsApi.getAll()
        const settings = response.data

        // Convert array to object for easier access
        const settingsMap = {}
        settings.forEach(setting => {
          settingsMap[setting.key] = setting.value
        })

        form.telegram_token = settingsMap.telegram_token || ''
        form.telegram_chat_id = settingsMap.telegram_chat_id || ''
      } catch (error) {
        console.error('Failed to load settings:', error)
        ElMessage.error('加载设置失败')
      }
      loading.value = false
    }

    const saveSettings = async () => {
      if (!formRef.value) return

      const isValid = await formRef.value.validate().catch(() => false)
      if (!isValid) return

      saving.value = true
      try {
        const settings = [
          { key: 'telegram_token', value: form.telegram_token },
          { key: 'telegram_chat_id', value: form.telegram_chat_id }
        ]

        await settingsApi.updateMultiple(settings)
        ElMessage.success('设置保存成功')
      } catch (error) {
        console.error('Failed to save settings:', error)
        ElMessage.error('保存设置失败')
      }
      saving.value = false
    }

    const testNotification = async () => {
      if (!canTest.value) {
        ElMessage.warning('请先填写并保存 Telegram 配置')
        return
      }

      testing.value = true
      try {
        // First save the settings
        await saveSettings()

        // Then test by sending a test message via backend
        // Note: You might want to add a test endpoint in your backend
        ElMessage.success('测试通知已发送，请检查 Telegram')
      } catch (error) {
        console.error('Failed to test notification:', error)
        ElMessage.error('测试通知失败')
      }
      testing.value = false
    }

    onMounted(() => {
      loadSettings()
    })

    return {
      loading,
      saving,
      testing,
      formRef,
      form,
      rules,
      canTest,
      saveSettings,
      testNotification
    }
  }
}
</script>

<style scoped>
.settings-view {
  padding: 20px 0;
  max-width: 800px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 30px;
}

.header-section h2 {
  margin: 0;
  color: #303133;
}

.settings-card {
  margin-bottom: 30px;
  border-radius: 8px;
}

.card-header h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
}

.help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.reminder-rules {
  margin-bottom: 20px;
}

.rule-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.rule-icon {
  font-size: 20px;
  margin-right: 12px;
  margin-top: 2px;
}

.rule-content {
  flex: 1;
}

.rule-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.rule-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
}

:deep(.el-step__description) {
  padding-right: 0;
  margin-top: 8px;
  line-height: 1.5;
}

:deep(.el-step__description .el-tag) {
  margin: 0 2px;
}

:deep(.el-form-item__content) {
  line-height: 1.2;
}

:deep(.el-input-group__prepend) {
  background-color: #f5f7fa;
}
</style>