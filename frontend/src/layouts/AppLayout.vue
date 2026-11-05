<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataAnalysis, FolderOpened, Plus, SwitchButton } from '@element-plus/icons-vue'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const roleLabels = {
  boss: '老板',
  department_head: '部门负责人',
  pmo: 'PMO',
  project_manager: '项目经理',
  member: '项目成员',
} as const

const roleLabel = computed(() => (auth.user ? roleLabels[auth.user.role] : ''))
const canCreateProject = computed(() => auth.user?.role === 'pmo')

function isActive(path: string) {
  return route.path === path || route.path.startsWith(`${path}/`)
}

async function logout() {
  auth.logout()
  await router.replace({ name: 'login' })
}
</script>

<template>
  <el-container class="app-layout">
    <el-aside width="232px" class="app-aside">
      <div class="brand">
        <div class="brand-mark">PM</div>
        <div>
          <strong>项目管理平台</strong>
          <span>大数据业务部</span>
        </div>
      </div>
      <nav class="app-nav" aria-label="主导航">
        <RouterLink class="nav-item" :class="{ active: isActive('/dashboard') }" to="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>管理驾驶舱</span>
        </RouterLink>
        <RouterLink class="nav-item" :class="{ active: isActive('/projects') }" to="/projects">
          <el-icon><FolderOpened /></el-icon>
          <span>项目台账</span>
        </RouterLink>
        <RouterLink v-if="canCreateProject" class="nav-item" :class="{ active: isActive('/projects/new') }" to="/projects/new">
          <el-icon><Plus /></el-icon>
          <span>新建项目</span>
        </RouterLink>
      </nav>
      <div class="aside-note">
        <span>阶段一</span>
        <p>项目台账与权限基础</p>
      </div>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <div class="header-context">内部项目管理</div>
        <div class="user-area">
          <div class="user-copy">
            <strong>{{ auth.user?.display_name }}</strong>
            <span>{{ roleLabel }}</span>
          </div>
          <el-button text :icon="SwitchButton" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="app-main">
        <div class="content-wrap">
          <RouterView />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #f4f6f8;
}

.app-aside {
  display: flex;
  flex-direction: column;
  padding: 20px 14px;
  color: #d8e2ed;
  background: #172536;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 10px 24px;
}

.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 8px;
  color: #fff;
  background: #2f80ed;
  font-size: 12px;
  font-weight: 700;
}

.brand strong,
.brand span,
.user-copy strong,
.user-copy span {
  display: block;
}

.brand strong {
  color: #fff;
  font-size: 14px;
}

.brand span {
  margin-top: 3px;
  color: #91a4ba;
  font-size: 12px;
}

.app-nav {
  display: grid;
  gap: 6px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  padding: 0 12px;
  border-radius: 6px;
  color: #aebed0;
  font-size: 14px;
}

.nav-item:hover,
.nav-item.active {
  color: #fff;
  background: #24405f;
}

.aside-note {
  margin-top: auto;
  padding: 14px 12px;
  border-top: 1px solid #2c4055;
  color: #91a4ba;
  font-size: 12px;
}

.aside-note span {
  color: #8cbaff;
}

.aside-note p {
  margin: 6px 0 0;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
  border-bottom: 1px solid #e4e9ef;
  background: #fff;
}

.header-context {
  color: #64748b;
  font-size: 13px;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 14px;
}

.user-copy {
  text-align: right;
}

.user-copy strong {
  color: #1f2937;
  font-size: 13px;
}

.user-copy span {
  margin-top: 2px;
  color: #64748b;
  font-size: 12px;
}

.app-main {
  padding: 28px;
}

.content-wrap {
  width: min(1240px, 100%);
  margin: 0 auto;
}

@media (max-width: 720px) {
  .app-aside {
    width: 72px !important;
    padding: 16px 8px;
  }

  .brand {
    justify-content: center;
    padding: 2px 0 20px;
  }

  .brand > div:last-child,
  .nav-item span,
  .aside-note {
    display: none;
  }

  .nav-item {
    justify-content: center;
    padding: 0;
  }

  .app-main {
    padding: 20px 14px;
  }
}
</style>

