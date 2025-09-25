# Subscription Management Panel | 订阅管理面板

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)

A lightweight, self-hosted subscription management panel that helps you track personal subscription services with intuitive calendar views and automated Telegram reminders.

一个轻量级的自托管订阅管理面板，帮助您管理个人订阅服务，提供直观的日历视图和自动化 Telegram 提醒功能。

[English](#english) | [中文](#中文)

---

## English

### 🚀 Features

#### **Core Functionality**
- ✅ **Subscription Management**: Create, read, update, and delete subscription services
- ✅ **Multiple View Modes**: Card view, list view, and table view for optimal data presentation
- ✅ **Advanced Sorting**: Sort by name, price, due date, or creation time with ascending/descending order
- ✅ **Smart Reminders**: Automated Telegram notifications 7, 3, and 1 day(s) before renewal
- ✅ **Calendar Integration**: Intuitive monthly calendar displaying all renewal dates
- ✅ **Extended Notes Support**: Rich text notes with up to 1000 characters, supporting formatting

#### **Multi-platform Support**
- ✅ **Multi-currency**: Support for CNY, USD, EUR, and other currencies
- ✅ **Flexible Billing Cycles**: Monthly, quarterly, and yearly subscription periods
- ✅ **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- ✅ **Cross-browser Compatibility**: Works seamlessly across modern web browsers

#### **Technical Excellence**
- ✅ **Data Persistence**: SQLite database with reliable data storage
- ✅ **Containerized Deployment**: Docker-based deployment with environment isolation
- ✅ **RESTful API**: Well-documented API endpoints with OpenAPI/Swagger integration
- ✅ **Real-time Updates**: Live data synchronization across all view modes

### 🛠 Technology Stack

#### **Backend Architecture**
- **Python + FastAPI**: High-performance, modern web framework with automatic API documentation
- **SQLModel**: Type-safe ORM with Pydantic integration for data validation
- **APScheduler**: Robust job scheduling for automated reminder notifications
- **python-telegram-bot**: Comprehensive Telegram Bot API integration
- **SQLite**: Lightweight, serverless database engine

#### **Frontend Framework**
- **Vue.js 3**: Progressive JavaScript framework with Composition API
- **Element Plus**: Enterprise-grade UI component library for Vue.js
- **Axios**: Promise-based HTTP client for API communication
- **Day.js**: Immutable date library with minimal footprint
- **Vite**: Next-generation frontend build tool with hot module replacement

#### **DevOps & Deployment**
- **Docker + Docker Compose**: Multi-container orchestration for seamless deployment
- **Nginx**: High-performance web server for static file serving and reverse proxy
- **Alpine Linux**: Security-focused, lightweight container base images

### 📦 Quick Start

#### **Prerequisites**
- Docker 20.10+ and Docker Compose 2.0+
- Minimum 512MB RAM and 1GB storage
- Network access for Telegram integration (optional)

#### **1. Clone Repository**
```bash
git clone <repository-url>
cd manage_my_service_subscription
```

#### **2. Create Data Directory**
```bash
mkdir -p data
chmod 755 data
```

#### **3. Deploy with Docker Compose**
```bash
docker compose up -d
```

#### **4. Access Application**
- **Frontend Interface**: http://localhost:3001
- **Backend API Documentation**: http://localhost:3000/docs
- **Health Check**: http://localhost:3000/health

### 🤖 Telegram Bot Configuration

#### **Step 1: Create Telegram Bot**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command and follow the prompts
3. Choose a name and username for your bot
4. Copy the provided Bot Token

#### **Step 2: Obtain Chat ID**
1. Search for `@userinfobot` in Telegram
2. Send any message to the bot
3. Copy the returned Chat ID (numeric value)

#### **Step 3: Configure in Application**
1. Navigate to the "Settings" page in the web interface
2. Enter your Bot Token and Chat ID
3. Click "Save Settings" to persist configuration
4. Use "Test Notification" to verify the setup

### 📊 View Modes & Sorting

The application offers three distinct view modes to suit different user preferences:

#### **Card View** 🎴
- Visual card-based layout with subscription details
- Ideal for quick overview and visual scanning
- Each card displays price, cycle, due date, and notes

#### **List View** 📋
- Compact list format for efficient browsing
- Optimized for mobile devices and smaller screens
- Displays key information in a condensed format

#### **Table View** 📊
- Tabular presentation for data comparison
- Sortable columns for enhanced data analysis
- Perfect for managing large subscription portfolios

#### **Sorting Capabilities**
- **By Name**: Alphabetical ordering
- **By Price**: Numerical value comparison
- **By Due Date**: Chronological sorting for payment planning
- **By Creation Date**: Track subscription addition order
- **Ascending/Descending**: Toggle sort direction with one click

### 💾 Data Management

#### **Database Backup**
```bash
# Create timestamped backup
cp ./data/subscription.db ./data/backup_$(date +%Y%m%d_%H%M%S).db

# Automated backup script
echo "0 2 * * * cp /path/to/data/subscription.db /path/to/backups/subscription_\$(date +\%Y\%m\%d).db" | crontab -
```

#### **Data Migration**
```bash
# Export data (requires jq)
curl -s http://localhost:3000/api/subscriptions | jq . > subscriptions_export.json

# Import data (custom script required)
./scripts/import_subscriptions.py subscriptions_export.json
```

### 🔧 Development Environment

#### **Backend Development**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### **Frontend Development**
```bash
cd frontend
npm install
npm run dev  # Development server with hot reload
npm run build  # Production build
npm run preview  # Preview production build
```

#### **API Documentation**
After starting the backend service, visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

### 🌍 Environment Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `DATABASE_URL` | `sqlite:///./data/subscription.db` | Database connection string |
| `TZ` | `UTC` | Timezone for scheduling and date display |
| `LOG_LEVEL` | `INFO` | Application logging level |

### 📋 System Requirements

- **Operating System**: Linux (recommended), macOS, Windows
- **Memory**: Minimum 512MB RAM, 1GB recommended
- **Storage**: Minimum 1GB available space
- **Network**: Internet connection for Telegram notifications
- **Browser**: Modern browser with JavaScript enabled

### 🤝 Contributing

We welcome contributions from the community! Please read our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

#### **What this means:**
- ✅ **Freedom to use**: Use the software for any purpose
- ✅ **Freedom to study**: Access and modify the source code
- ✅ **Freedom to distribute**: Share copies with others
- ✅ **Freedom to improve**: Distribute modified versions
- ⚠️ **Copyleft requirement**: Derivative works must also be GPL-licensed

### 🆘 Support & Issues

- **Bug Reports**: [GitHub Issues](https://github.com/your-repo/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Documentation**: [Wiki](https://github.com/your-repo/wiki)

---

## 中文

### 🚀 功能特性

#### **核心功能**
- ✅ **订阅管理**: 创建、查看、更新和删除订阅服务
- ✅ **多种视图模式**: 卡片视图、列表视图和表格视图，优化数据展示
- ✅ **高级排序**: 按名称、价格、到期日或创建时间排序，支持升序/降序
- ✅ **智能提醒**: 续费前 7天、3天、1天自动发送 Telegram 通知
- ✅ **日历集成**: 直观的月度日历显示所有续费日期
- ✅ **扩展备注支持**: 支持最多1000字符的富文本备注，包含格式化

#### **多平台支持**
- ✅ **多货币支持**: 支持人民币、美元、欧元等多种货币
- ✅ **灵活计费周期**: 月度、季度、年度订阅周期
- ✅ **响应式设计**: 针对桌面、平板和移动设备优化
- ✅ **跨浏览器兼容**: 在现代网络浏览器中无缝运行

#### **技术卓越**
- ✅ **数据持久化**: SQLite 数据库，可靠的数据存储
- ✅ **容器化部署**: 基于 Docker 的部署，环境隔离
- ✅ **RESTful API**: 文档完善的 API 端点，集成 OpenAPI/Swagger
- ✅ **实时更新**: 所有视图模式下的实时数据同步

### 🛠 技术架构

#### **后端架构**
- **Python + FastAPI**: 高性能现代 Web 框架，自动 API 文档生成
- **SQLModel**: 类型安全的 ORM，集成 Pydantic 数据验证
- **APScheduler**: 健壮的任务调度，用于自动提醒通知
- **python-telegram-bot**: 全面的 Telegram Bot API 集成
- **SQLite**: 轻量级无服务器数据库引擎

#### **前端框架**
- **Vue.js 3**: 渐进式 JavaScript 框架，采用组合式 API
- **Element Plus**: Vue.js 的企业级 UI 组件库
- **Axios**: 基于 Promise 的 HTTP 客户端，用于 API 通信
- **Day.js**: 不可变日期库，体积小巧
- **Vite**: 下一代前端构建工具，支持热模块替换

#### **运维与部署**
- **Docker + Docker Compose**: 多容器编排，无缝部署
- **Nginx**: 高性能 Web 服务器，用于静态文件服务和反向代理
- **Alpine Linux**: 安全导向的轻量级容器基础镜像

### 📦 快速开始

#### **系统要求**
- Docker 20.10+ 和 Docker Compose 2.0+
- 最低 512MB 内存和 1GB 存储空间
- 网络访问（Telegram 集成需要，可选）

#### **1. 克隆仓库**
```bash
git clone <仓库地址>
cd manage_my_service_subscription
```

#### **2. 配置环境变量（可选）**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

**常用配置示例：**
```bash
# 自定义端口
BACKEND_PORT=8080
FRONTEND_PORT=8000

# 时区配置
TZ=Asia/Shanghai

# 日志级别
LOG_LEVEL=WARNING
```

#### **3. 创建数据目录**
```bash
mkdir -p data
chmod 755 data
```

#### **4. 使用 Docker Compose 部署**
```bash
docker compose up -d
```

#### **5. 访问应用**
- **前端界面**: http://localhost:${FRONTEND_PORT:-3001}
- **后端 API 文档**: http://localhost:${BACKEND_PORT:-3000}/docs
- **健康检查**: http://localhost:${BACKEND_PORT:-3000}/health

**默认端口：**
- 前端：3001
- 后端：3000

**如果使用自定义端口，请相应调整URL**

### 🤖 Telegram 机器人配置

#### **步骤 1: 创建 Telegram 机器人**
1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令并按提示操作
3. 为您的机器人选择名称和用户名
4. 复制提供的 Bot Token

#### **步骤 2: 获取 Chat ID**
1. 在 Telegram 中搜索 `@userinfobot`
2. 向机器人发送任意消息
3. 复制返回的 Chat ID（数字值）

#### **步骤 3: 在应用中配置**
1. 在 Web 界面中导航到"设置"页面
2. 输入您的 Bot Token 和 Chat ID
3. 点击"保存设置"以持久化配置
4. 使用"测试通知"验证设置

### 📊 视图模式与排序

应用提供三种不同的视图模式以适应不同用户偏好：

#### **卡片视图** 🎴
- 基于视觉卡片的布局，展示订阅详情
- 适合快速概览和视觉扫描
- 每张卡片显示价格、周期、到期日和备注

#### **列表视图** 📋
- 紧凑的列表格式，便于高效浏览
- 针对移动设备和小屏幕优化
- 以压缩格式显示关键信息

#### **表格视图** 📊
- 表格展示便于数据对比
- 可排序列增强数据分析
- 适合管理大型订阅组合

#### **排序功能**
- **按名称**: 字母顺序排列
- **按价格**: 数值大小比较
- **按到期日**: 按时间顺序排序，便于付款规划
- **按创建日期**: 跟踪订阅添加顺序
- **升序/降序**: 一键切换排序方向

### 💾 数据管理

#### **数据库备份**
```bash
# 创建带时间戳的备份
cp ./data/subscription.db ./data/backup_$(date +%Y%m%d_%H%M%S).db

# 自动备份脚本
echo "0 2 * * * cp /path/to/data/subscription.db /path/to/backups/subscription_\$(date +\%Y\%m\%d).db" | crontab -
```

#### **数据迁移**
```bash
# 导出数据（需要 jq）
curl -s http://localhost:3000/api/subscriptions | jq . > subscriptions_export.json

# 导入数据（需要自定义脚本）
./scripts/import_subscriptions.py subscriptions_export.json
```

### 🔧 开发环境

#### **后端开发**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### **前端开发**
```bash
cd frontend
npm install
npm run dev  # 开发服务器，支持热重载
npm run build  # 生产构建
npm run preview  # 预览生产构建
```

#### **API 文档**
启动后端服务后，访问 http://localhost:8000/docs 查看由 Swagger UI 提供的交互式 API 文档。

### 🌍 环境变量配置

| 变量名 | 默认值 | 描述 |
|--------|--------|------|
| `BACKEND_PORT` | `3000` | 后端API服务端口 |
| `FRONTEND_PORT` | `3001` | 前端Web服务端口 |
| `DATABASE_URL` | `sqlite:///./data/subscription.db` | 数据库连接字符串 |
| `TZ` | `UTC` | 用于调度和日期显示的时区 |
| `LOG_LEVEL` | `INFO` | 应用程序日志级别 |

**注：** CORS已配置为允许所有来源访问，无需额外配置。

### 🚀 部署到不同环境

#### **开发环境**
```bash
# .env
BACKEND_PORT=8080
FRONTEND_PORT=3000
LOG_LEVEL=DEBUG
```

#### **生产环境**
```bash
# .env
BACKEND_PORT=8000
FRONTEND_PORT=80
TZ=Asia/Shanghai
LOG_LEVEL=WARNING
```

#### **VPS部署（自定义端口）**
```bash
# .env
BACKEND_PORT=8888
FRONTEND_PORT=9999
TZ=Asia/Shanghai
LOG_LEVEL=INFO
```

**部署提示：**
- 生产环境建议设置合适的时区
- 根据需要调整日志级别
- 使用反向代理（如Nginx）配置HTTPS
- CORS已自动配置，支持任何域名访问

### 📋 系统要求

- **操作系统**: Linux（推荐）、macOS、Windows
- **内存**: 最低 512MB RAM，推荐 1GB
- **存储**: 最低 1GB 可用空间
- **网络**: 需要互联网连接以支持 Telegram 通知
- **浏览器**: 支持 JavaScript 的现代浏览器

### 🤝 贡献指南

我们欢迎社区贡献！请阅读我们的贡献指南：

1. Fork 这个仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

### 📄 开源许可证

本项目采用 GNU 通用公共许可证 v3.0 - 详情请参阅 [LICENSE](LICENSE) 文件。

#### **这意味着什么：**
- ✅ **使用自由**: 可用于任何目的
- ✅ **学习自由**: 可访问和修改源代码
- ✅ **分发自由**: 可与他人分享副本
- ✅ **改进自由**: 可分发修改版本
- ⚠️ **Copyleft 要求**: 衍生作品也必须采用 GPL 许可证

### 🆘 支持与问题

- **错误报告**: [GitHub Issues](https://github.com/your-repo/issues)
- **功能请求**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **文档**: [Wiki](https://github.com/your-repo/wiki)

---

<div align="center">

**[⬆ Back to Top | 返回顶部](#subscription-management-panel--订阅管理面板)**

Made with ❤️ by developers, for developers.
由开发者制作，为开发者服务。

</div>