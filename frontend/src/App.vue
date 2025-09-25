<template>
  <div id="app">
    <el-container class="layout-container">
      <el-header class="header">
        <div class="header-content">
          <h1 class="title">订阅管理面板</h1>
          <el-menu
            :default-active="$route.path"
            class="nav-menu"
            mode="horizontal"
            router
          >
            <el-menu-item index="/">
              <el-icon><List /></el-icon>
              <span>订阅列表</span>
            </el-menu-item>
            <el-menu-item index="/calendar">
              <el-icon><Calendar /></el-icon>
              <span>日历视图</span>
            </el-menu-item>
            <el-menu-item index="/analytics">
              <el-icon><DataAnalysis /></el-icon>
              <span>趋势分析</span>
            </el-menu-item>
            <el-menu-item index="/settings">
              <el-icon><Setting /></el-icon>
              <span>设置</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.layout-container {
  min-height: 100vh;
}

.header {
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  width: 100%;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  height: 100%;
}

.title {
  margin: 0 40px 0 0;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.nav-menu {
  border-bottom: none;
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  width: 100%;
  min-height: calc(100vh - 60px);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}
</style>