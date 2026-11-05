<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

import { createProject, fetchDepartments, fetchProjectManagers } from '@/api/projects'
import { getErrorMessage } from '@/api/http'
import ProjectForm, { type ProjectFormState } from '@/components/ProjectForm.vue'
import { useAuthStore } from '@/stores/auth'
import type { DepartmentOption, UserOption } from '@/types/project'

const router = useRouter()
const auth = useAuthStore()
const departments = ref<DepartmentOption[]>([])
const managers = ref<UserOption[]>([])
const loading = ref(false)
const loadingOptions = ref(false)
const form = reactive<ProjectFormState>({
  code: '',
  name: '',
  description: '',
  department_id: undefined,
  project_manager_id: undefined,
  client_name: '',
  region: '',
  planned_start_date: '',
  planned_end_date: '',
  seafile_url: '',
})

async function loadManagers(departmentId?: number) {
  form.project_manager_id = undefined
  if (!departmentId) {
    managers.value = []
    return
  }
  loadingOptions.value = true
  try {
    managers.value = await fetchProjectManagers(departmentId)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '项目经理选项加载失败'))
  } finally {
    loadingOptions.value = false
  }
}

async function loadOptions() {
  loadingOptions.value = true
  try {
    departments.value = await fetchDepartments()
    form.department_id = departments.value[0]?.id
    await loadManagers(form.department_id)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '项目选项加载失败'))
  } finally {
    loadingOptions.value = false
  }
}

async function submit(value: ProjectFormState) {
  loading.value = true
  try {
    const project = await createProject({
      ...value,
      department_id: value.department_id!,
      project_manager_id: value.project_manager_id!,
      seafile_url: value.seafile_url || undefined,
    })
    ElMessage.success('项目创建成功')
    await router.replace(`/projects/${project.id}`)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '项目创建失败'))
  } finally {
    loading.value = false
  }
}

onMounted(loadOptions)
</script>

<template>
  <div v-if="auth.user?.role !== 'pmo'" class="empty-page">
    <el-result icon="warning" title="没有新建项目权限" sub-title="新项目由 PMO 统一创建" />
  </div>
  <template v-else>
    <div class="page-header">
      <div>
        <h1>新建项目</h1>
        <p>先建立项目基线，阶段、模块和进度将在下一阶段维护。</p>
      </div>
      <div class="page-actions"><el-button :icon="ArrowLeft" @click="router.push('/projects')">返回台账</el-button></div>
    </div>
    <el-card v-loading="loadingOptions" shadow="never">
      <ProjectForm :model-value="form" :departments="departments" :managers="managers" :loading="loading" @submit="submit" @cancel="router.push('/projects')" @department-change="loadManagers" />
    </el-card>
  </template>
</template>

<style scoped>
.empty-page { display: grid; min-height: 50vh; place-items: center; }
</style>

