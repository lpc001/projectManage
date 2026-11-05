<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowRight, Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

import { fetchProjects } from '@/api/projects'
import { getErrorMessage } from '@/api/http'
import ProjectStatusTag from '@/components/ProjectStatusTag.vue'
import type { ProjectListItem } from '@/types/project'

const router = useRouter()
const projects = ref<ProjectListItem[]>([])
const loading = ref(true)

const counts = computed(() => ({
  total: projects.value.length,
  active: projects.value.filter((project) => project.lifecycle_status === 'active').length,
  planning: projects.value.filter((project) => project.lifecycle_status === 'planning').length,
  attention: projects.value.filter((project) => ['paused', 'completed'].includes(project.lifecycle_status)).length,
}))

async function loadProjects() {
  loading.value = true
  try {
    projects.value = await fetchProjects()
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

onMounted(loadProjects)
</script>

<template>
  <div class="page-header">
    <div>
      <h1>管理驾驶舱</h1>
      <p>快速掌握当前可见项目的基础状态，进度和风险指标将在后续阶段加入。</p>
    </div>
    <div class="page-actions">
      <el-button :icon="Refresh" :loading="loading" @click="loadProjects">刷新</el-button>
      <el-button type="primary" :icon="ArrowRight" @click="router.push('/projects')">查看项目台账</el-button>
    </div>
  </div>

  <div v-loading="loading" class="dashboard-content">
    <div class="metric-grid">
      <el-card shadow="never"><div class="metric-value">{{ counts.total }}</div><div class="metric-label">可见项目</div></el-card>
      <el-card shadow="never"><div class="metric-value metric-success">{{ counts.active }}</div><div class="metric-label">执行中</div></el-card>
      <el-card shadow="never"><div class="metric-value metric-info">{{ counts.planning }}</div><div class="metric-label">筹备中</div></el-card>
      <el-card shadow="never"><div class="metric-value metric-warning">{{ counts.attention }}</div><div class="metric-label">暂停或已完成</div></el-card>
    </div>

    <el-card shadow="never" class="dashboard-table">
      <template #header>
        <div class="section-heading">
          <strong>最近更新项目</strong>
          <el-button text :icon="ArrowRight" @click="router.push('/projects')">全部项目</el-button>
        </div>
      </template>
      <el-empty v-if="!loading && !projects.length" description="暂无可见项目" />
      <el-table v-else :data="projects.slice(0, 5)" row-key="id">
        <el-table-column prop="code" label="项目编码" width="150" />
        <el-table-column prop="name" label="项目名称" min-width="220" />
        <el-table-column prop="project_manager_name" label="项目经理" width="140" />
        <el-table-column label="状态" width="120"><template #default="scope"><ProjectStatusTag :status="scope.row.lifecycle_status" /></template></el-table-column>
        <el-table-column prop="planned_end_date" label="计划结束" width="140" />
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.metric-success { color: #1f9d68; }
.metric-info { color: #3c82d6; }
.metric-warning { color: #c98522; }
.dashboard-table { margin-top: 20px; }
.section-heading { display: flex; align-items: center; justify-content: space-between; }
</style>

