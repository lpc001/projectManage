<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'

import { getErrorMessage } from '@/api/http'
import { createSystemUser, disableSystemUser, listSystemDepartments, listSystemRoles, listSystemUsers } from '@/api/systemAdmin'
import type { SystemDepartment, SystemRole, SystemUser } from '@/types/system'

const users = ref<SystemUser[]>([])
const roles = ref<SystemRole[]>([])
const departments = ref<SystemDepartment[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ username: '', display_name: '', password: '', department_id: undefined as number | undefined, role_ids: [] as number[] })

async function load() {
  loading.value = true
  try {
    const [userRows, roleRows, departmentRows] = await Promise.all([listSystemUsers(), listSystemRoles(), listSystemDepartments()])
    users.value = userRows
    roles.value = roleRows
    departments.value = departmentRows
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '系统用户加载失败'))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { username: '', display_name: '', password: '', department_id: departments.value[0]?.id, role_ids: [] })
  dialogVisible.value = true
}

async function submit() {
  if (!form.department_id || !form.username || !form.display_name || !form.password) {
    ElMessage.warning('请填写完整的用户信息')
    return
  }
  try {
    await createSystemUser({ ...form, department_id: form.department_id })
    ElMessage.success('用户创建成功')
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '用户创建失败'))
  }
}

async function disable(user: SystemUser) {
  try {
    await ElMessageBox.confirm(`确认停用用户“${user.display_name}”吗？`, '停用用户', { type: 'warning' })
    await disableSystemUser(user.id)
    ElMessage.success('用户已停用')
    await load()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(getErrorMessage(error, '用户停用失败'))
  }
}

onMounted(load)
</script>

<template>
  <div class="page-header">
    <div><h1>用户管理</h1><p>维护账号状态、所属部门和角色分配。</p></div>
    <div class="page-actions"><el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button><el-button type="primary" :icon="Plus" @click="openCreate">新建用户</el-button></div>
  </div>
  <el-card shadow="never">
    <el-table v-loading="loading" :data="users" row-key="id">
      <el-table-column prop="username" label="登录名" min-width="220" />
      <el-table-column prop="display_name" label="显示名" width="150" />
      <el-table-column label="角色" min-width="220"><template #default="scope"><el-tag v-for="role in scope.row.roles" :key="role.code" size="small" class="role-tag">{{ role.name }}</el-tag><span v-if="!scope.row.roles.length" class="muted">未分配</span></template></el-table-column>
      <el-table-column label="状态" width="100"><template #default="scope"><el-tag :type="scope.row.is_active ? 'success' : 'info'">{{ scope.row.is_active ? '启用' : '停用' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="110"><template #default="scope"><el-button v-if="scope.row.is_active" text type="danger" @click="disable(scope.row)">停用</el-button></template></el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" title="新建用户" width="520px">
    <el-form label-position="top">
      <el-form-item label="登录名"><el-input v-model="form.username" placeholder="例如 user@example.com" /></el-form-item>
      <el-form-item label="显示名"><el-input v-model="form.display_name" /></el-form-item>
      <el-form-item label="初始密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
      <el-form-item label="主部门"><el-select v-model="form.department_id" class="full-width"><el-option v-for="department in departments" :key="department.id" :label="department.name" :value="department.id" /></el-select></el-form-item>
      <el-form-item label="角色"><el-select v-model="form.role_ids" multiple class="full-width"><el-option v-for="role in roles.filter((item) => item.is_active)" :key="role.id" :label="role.name" :value="role.id" /></el-select></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submit">创建</el-button></template>
  </el-dialog>
</template>

<style scoped>
.role-tag { margin: 2px 4px 2px 0; }
.muted { color: #94a3b8; }
.full-width { width: 100%; }
</style>

