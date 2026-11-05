<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { CircleClose, CircleCheck } from '@element-plus/icons-vue'

import type { DepartmentOption, UserOption } from '@/types/project'

export interface ProjectFormState {
  code: string
  name: string
  description: string
  department_id: number | undefined
  project_manager_id: number | undefined
  client_name: string
  region: string
  planned_start_date: string
  planned_end_date: string
  seafile_url: string
}

const props = defineProps<{
  modelValue: ProjectFormState
  departments: DepartmentOption[]
  managers: UserOption[]
  loading: boolean
  isEdit?: boolean
}>()

const emit = defineEmits<{
  submit: [value: ProjectFormState]
  cancel: []
  departmentChange: [value: number | undefined]
}>()

const form = reactive<ProjectFormState>({ ...props.modelValue })

watch(
  () => props.modelValue,
  (value) => Object.assign(form, value),
  { deep: true },
)

function handleSubmit() {
  if (!form.department_id || !form.project_manager_id || !form.planned_start_date || !form.planned_end_date) {
    ElMessage.warning('请先填写部门、项目经理和计划日期')
    return
  }
  if (form.planned_end_date < form.planned_start_date) {
    ElMessage.warning('计划结束日期不能早于计划开始日期')
    return
  }
  emit('submit', { ...form })
}
</script>

<template>
  <el-form label-position="top" class="project-form" @submit.prevent="handleSubmit">
    <div class="form-grid">
      <el-form-item label="项目编码" required>
        <el-input v-model="form.code" :disabled="isEdit" placeholder="例如 PM-2026-001" />
      </el-form-item>
      <el-form-item label="项目名称" required>
        <el-input v-model="form.name" placeholder="请输入项目名称" />
      </el-form-item>
      <el-form-item label="所属部门" required>
        <el-select
          v-model="form.department_id"
          class="full-width"
          placeholder="请选择部门"
          @change="emit('departmentChange', form.department_id)"
        >
          <el-option v-for="department in departments" :key="department.id" :label="department.name" :value="department.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="项目经理" required>
        <el-select v-model="form.project_manager_id" class="full-width" placeholder="请选择项目经理">
          <el-option v-for="manager in managers" :key="manager.id" :label="manager.display_name" :value="manager.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="计划开始日期" required>
        <el-date-picker v-model="form.planned_start_date" class="full-width" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item label="计划结束日期" required>
        <el-date-picker v-model="form.planned_end_date" class="full-width" type="date" value-format="YYYY-MM-DD" />
      </el-form-item>
      <el-form-item label="客户名称">
        <el-input v-model="form.client_name" placeholder="请输入客户或业务单位" />
      </el-form-item>
      <el-form-item label="执行地区">
        <el-input v-model="form.region" placeholder="例如 华东" />
      </el-form-item>
      <el-form-item label="Seafile 材料链接" class="span-2">
        <el-input v-model="form.seafile_url" placeholder="https://..." />
      </el-form-item>
      <el-form-item label="项目说明" class="span-2">
        <el-input v-model="form.description" type="textarea" :rows="4" placeholder="记录项目目标、范围或关键说明" />
      </el-form-item>
    </div>
    <div class="form-actions">
      <el-button :icon="CircleClose" @click="emit('cancel')">取消</el-button>
      <el-button type="primary" :icon="CircleCheck" :loading="loading" @click="handleSubmit">
        {{ isEdit ? '保存修改' : '创建项目' }}
      </el-button>
    </div>
  </el-form>
</template>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 20px;
}

.span-2 {
  grid-column: span 2;
}

.full-width {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

@media (max-width: 680px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: auto;
  }
}
</style>

