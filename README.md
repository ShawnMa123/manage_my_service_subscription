# 订阅管理面板

一个轻量级的自托管订阅管理面板，帮助您管理个人订阅服务，通过日历视图直观查看续费日期，并通过 Telegram Bot 接收续费提醒。

## 功能特性

- ✅ **订阅管理**: 添加、编辑、删除和查看订阅服务
- ✅ **智能提醒**: 在续费前 7天、3天、1天自动发送 Telegram 提醒
- ✅ **日历视图**: 直观的月度日历显示所有续费日期
- ✅ **多货币支持**: 支持人民币、美元、欧元等货币
- ✅ **多种周期**: 支持月度、季度、年度续费周期
- ✅ **数据持久化**: 使用 SQLite 数据库，数据安全可靠
- ✅ **Docker 部署**: 一键启动，环境隔离

## 技术栈

### 后端
- **Python + FastAPI**: 高性能 API 框架
- **SQLModel**: 现代 ORM，类型安全
- **APScheduler**: 定时任务调度
- **python-telegram-bot**: Telegram 机器人集成

### 前端
- **Vue.js 3**: 现代前端框架
- **Element Plus**: 高质量 UI 组件库
- **Axios**: HTTP 客户端
- **Day.js**: 轻量级日期处理

### 部署
- **Docker + Docker Compose**: 容器化部署
- **Nginx**: 静态文件服务和反向代理

## 快速开始

### 1. 创建数据目录

```bash
mkdir -p data
```

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 访问应用

- 前端界面: http://localhost:8080
- 后端 API 文档: http://localhost:8000/docs

## Telegram 配置

### 1. 创建 Telegram Bot

1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置 Bot 名称和用户名
4. 复制获得的 Bot Token

### 2. 获取 Chat ID

1. 在 Telegram 中搜索 `@userinfobot`
2. 向它发送任意消息
3. 复制返回的 Chat ID 数字

### 3. 在应用中配置

1. 访问应用的"设置"页面
2. 填入 Bot Token 和 Chat ID
3. 点击"保存设置"
4. 点击"测试通知"验证配置

## 数据备份

数据库文件位于 `./data/database.db`，定期备份此文件即可保证数据安全。

```bash
# 备份数据库
cp ./data/database.db ./data/database_backup_$(date +%Y%m%d).db
```

## 开发模式

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的 API 文档。

## 环境变量

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `DATABASE_URL` | `sqlite:///./data/database.db` | 数据库连接字符串 |

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 512MB 内存
- 至少 1GB 存储空间

## 许可证

MIT License

## 支持

如果您遇到问题或有功能建议，请提交 Issue。