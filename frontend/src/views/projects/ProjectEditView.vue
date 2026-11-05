<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchDepartments, fetchProject, fetchProjectManagers, updateProject } from '@/api/projects'
import { getErrorMessage } from '@/api/http'
import ProjectForm, { type ProjectFormState } from '@/components/ProjectForm.vue'
import { useAuthStore } from '@/stores/auth'
import type { DepartmentOption, UserOption } from '@/types/project'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const departments = ref<DepartmentOption[]>([])
const managers = ref<UserOption[]>([])
const loading = ref(true)
const saving = ref(false)
const form = reactive<ProjectFormState>({
  code: '', name: '', description: '', department_id: undefined, project_manager_id: undefined,
  client_name: '', region: '', planned_start_date: '', planned_end_date: '', seafile_url: '',
})

async function loadManagers(departmentId?: number, keepManager = false) {
  if (!departmentId) { managers.value = []; return }
  try {
    managers.value = await fetchProjectManagers(departmentId)
    if (!keepManager || !managers.value.some((manager) => manager.id === form.project_manager_id)) form.project_manager_id = undefined
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '项目经理选项加载失败'))
  }
}

async function load() {
  try {
    const [project, departmentOptions] = await Promise.all([
      fetchProject(Number(route.params.id), true),
      fetchDepartments(),
    ])
    departments.value = departmentOptions
    Object.assign(form, {
      code: project.code,
      name: project.name,
      description: project.description || '',
      department_id: project.department_id,
      project_manager_id: project.project_manager_id,
      client_name: project.client_name || '',
      region: project.region || '',
      planned_start_date: project.planned_start_date,
      planned_end_date: project.planned_end_date,
      seafile_url: project.seafile_url || '',
    })
    await loadManagers(form.department_id, true)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '项目加载失败'))
  } finally {
    loading.value = false
  }
}

async function submit(value: ProjectFormState) {
  saving.value = true
  try {
    await updateProject(Number(route.params.id), {
      ...value,
      department_id: value.department_id!,
      project_manager_id: value.project_manager_id!,
      seafile_url: value.seafile_url || undefined,
    })
    ElMessage.success('项目已更新')
    await router.replace(`/projects/${route.params.id}`)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '项目更新失败'))
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div v-if="!auth.hasPermission('project:update')" class="empty-page">
    <el-result icon="warning" title="没有编辑项目权限" />
  </div>
  <template v-else>
    <div class="page-header">
      <div><h1>编辑项目</h1><p>调整项目基线信息，项目进度和分项将在后续阶段维护。</p></div>
      <div class="page-actions"><el-button :icon="ArrowLeft" @click="router.push(`/projects/${route.params.id}`)">返回详情</el-button></div>
    </div>
    <el-card v-loading="loading" shadow="never">
      <ProjectForm v-if="!loading" :model-value="form" :departments="departments" :managers="managers" :loading="saving" is-edit @submit="submit" @cancel="router.push(`/projects/${route.params.id}`)" @department-change="(value) => loadManagers(value)" />
    </el-card>
  </template>
</template>

<style scoped>
.empty-page { display: grid; min-height: 50vh; place-items: center; }
</style>

