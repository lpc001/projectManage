<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

import { fetchProjects } from '@/api/projects'
import { getErrorMessage } from '@/api/http'
import ProjectStatusTag from '@/components/ProjectStatusTag.vue'
import { useAuthStore } from '@/stores/auth'
import type { ProjectLifecycleStatus, ProjectListItem } from '@/types/project'

const router = useRouter()
const auth = useAuthStore()
const projects = ref<ProjectListItem[]>([])
const loading = ref(false)
const keyword = ref('')
const status = ref<ProjectLifecycleStatus | ''>('')
const includeArchived = ref(false)

const filteredProjects = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase()
  return projects.value.filter((project) => {
    const matchesKeyword = !normalizedKeyword || `${project.code} ${project.name}`.toLowerCase().includes(normalizedKeyword)
    const matchesStatus = !status.value || project.lifecycle_status === status.value
    return matchesKeyword && matchesStatus
  })
})

async function loadProjects() {
  loading.value = true
  try {
    projects.value = await fetchProjects(includeArchived.value)
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    loading.value = false
  }
}

function openProject(project: ProjectListItem) {
  router.push(`/projects/${project.id}`)
}

onMounted(loadProjects)
</script>

<template>
  <div class="page-header">
    <div>
      <h1>项目台账</h1>
      <p>统一维护项目基线，后续阶段将在这里下钻到阶段、模块和进度。</p>
    </div>
    <div class="page-actions">
      <el-button :icon="Refresh" :loading="loading" @click="loadProjects">刷新</el-button>
      <el-button v-if="auth.hasPermission('project:create')" type="primary" :icon="Plus" @click="router.push('/projects/new')">新建项目</el-button>
    </div>
  </div>

  <el-card shadow="never">
    <div class="filter-bar">
      <el-input v-model="keyword" clearable :prefix-icon="Search" placeholder="搜索项目编码或名称" style="max-width: 300px" />
      <el-select v-model="status" clearable placeholder="全部状态" style="width: 150px">
        <el-option label="筹备中" value="planning" />
        <el-option label="执行中" value="active" />
        <el-option label="已完成" value="completed" />
        <el-option label="已暂停" value="paused" />
        <el-option v-if="auth.hasPermission('project:archive')" label="已归档" value="archived" />
      </el-select>
      <el-checkbox v-if="auth.hasPermission('project:archive')" v-model="includeArchived" @change="loadProjects">查看已归档</el-checkbox>
    </div>

    <el-table v-loading="loading" :data="filteredProjects" row-key="id" empty-text="暂无符合条件的项目" @row-click="openProject">
      <el-table-column prop="code" label="项目编码" width="155" />
      <el-table-column prop="name" label="项目名称" min-width="240" show-overflow-tooltip />
      <el-table-column prop="project_manager_name" label="项目经理" width="140" />
      <el-table-column label="状态" width="120"><template #default="scope"><ProjectStatusTag :status="scope.row.lifecycle_status" /></template></el-table-column>
      <el-table-column prop="planned_end_date" label="计划结束" width="140" />
      <el-table-column prop="updated_at" label="最近更新" width="180" />
      <el-table-column label="操作" width="100" fixed="right"><template #default="scope"><el-button text type="primary" @click.stop="openProject(scope.row)">详情</el-button></template></el-table-column>
    </el-table>
  </el-card>
</template>

