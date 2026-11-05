<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Key, Plus, Refresh } from '@element-plus/icons-vue'

import { getErrorMessage } from '@/api/http'
import { createSystemUser, disableSystemUser, listSystemDepartments, listSystemRoles, listSystemUsers, resetSystemUserPassword, setSystemUserRoles, updateSystemUser } from '@/api/systemAdmin'
import type { SystemDepartment, SystemRole, SystemUser } from '@/types/system'

const users = ref<SystemUser[]>([])
const roles = ref<SystemRole[]>([])
const departments = ref<SystemDepartment[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const resetDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const selectedUser = ref<SystemUser | null>(null)
const form = reactive({ username: '', display_name: '', password: '', department_id: undefined as number | undefined, role_ids: [] as number[], is_active: true })
const resetForm = reactive({ password: '' })

async function load() {
  loading.value = true
  try {
    const [userRows, roleRows, departmentRows] = await Promise.all([listSystemUsers(), listSystemRoles(), listSystemDepartments()])
    users.value = userRows
    roles.value = roleRows
    departments.value = departmentRows
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '系统用户加载失败'))
  } finally { loading.value = false }
}

function openCreate() {
  dialogMode.value = 'create'
  selectedUser.value = null
  Object.assign(form, { username: '', display_name: '', password: '', department_id: departments.value[0]?.id, role_ids: [], is_active: true })
  dialogVisible.value = true
}

function openEdit(user: SystemUser) {
  dialogMode.value = 'edit'
  selectedUser.value = user
  Object.assign(form, {
    username: user.username,
    display_name: user.display_name,
    password: '',
    department_id: user.department_id,
    role_ids: user.roles.map((role) => roles.value.find((item) => item.code === role.code)?.id).filter((id): id is number => id !== undefined),
    is_active: user.is_active,
  })
  dialogVisible.value = true
}

function openReset(user: SystemUser) {
  selectedUser.value = user
  resetForm.password = ''
  resetDialogVisible.value = true
}

async function submit() {
  if (!form.department_id || !form.display_name || (dialogMode.value === 'create' && (!form.username || !form.password))) {
    ElMessage.warning('请填写完整的用户信息')
    return
  }
  try {
    if (dialogMode.value === 'create') {
      await createSystemUser({ username: form.username, display_name: form.display_name, password: form.password, department_id: form.department_id, role_ids: form.role_ids })
      ElMessage.success('用户创建成功')
    } else if (selectedUser.value) {
      await updateSystemUser(selectedUser.value.id, { display_name: form.display_name, department_id: form.department_id, is_active: form.is_active })
      await setSystemUserRoles(selectedUser.value.id, form.role_ids)
      ElMessage.success('用户信息已更新')
    }
    dialogVisible.value = false
    await load()
  } catch (error) { ElMessage.error(getErrorMessage(error, '用户保存失败')) }
}

async function resetPassword() {
  if (!selectedUser.value || resetForm.password.length < 8) {
    ElMessage.warning('新密码至少需要 8 位')
    return
  }
  try {
    await resetSystemUserPassword(selectedUser.value.id, resetForm.password)
    ElMessage.success('密码已重置，原有登录会话已失效')
    resetDialogVisible.value = false
  } catch (error) { ElMessage.error(getErrorMessage(error, '密码重置失败')) }
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
  <div class="page-header"><div><h1>用户管理</h1><p>维护账号状态、所属部门和角色分配。</p></div><div class="page-actions"><el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button><el-button type="primary" :icon="Plus" @click="openCreate">新建用户</el-button></div></div>
  <el-card shadow="never">
    <el-table v-loading="loading" :data="users" row-key="id">
      <el-table-column prop="username" label="登录名" min-width="220" />
      <el-table-column prop="display_name" label="显示名" width="150" />
      <el-table-column label="角色" min-width="220"><template #default="scope"><el-tag v-for="role in scope.row.roles" :key="role.code" size="small" class="role-tag">{{ role.name }}</el-tag><span v-if="!scope.row.roles.length" class="muted">未分配</span></template></el-table-column>
      <el-table-column label="状态" width="100"><template #default="scope"><el-tag :type="scope.row.is_active ? 'success' : 'info'">{{ scope.row.is_active ? '启用' : '停用' }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="260" fixed="right"><template #default="scope"><el-button text type="primary" :icon="Edit" @click="openEdit(scope.row)">编辑</el-button><el-button text type="warning" :icon="Key" @click="openReset(scope.row)">重置密码</el-button><el-button v-if="scope.row.is_active" text type="danger" @click="disable(scope.row)">停用</el-button></template></el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新建用户' : '编辑用户'" width="520px">
    <el-form label-position="top"><el-form-item label="登录名"><el-input v-model="form.username" :disabled="dialogMode === 'edit'" placeholder="例如 user@example.com" /></el-form-item><el-form-item label="显示名"><el-input v-model="form.display_name" /></el-form-item><el-form-item v-if="dialogMode === 'create'" label="初始密码"><el-input v-model="form.password" type="password" show-password /></el-form-item><el-form-item label="主部门"><el-select v-model="form.department_id" class="full-width"><el-option v-for="department in departments" :key="department.id" :label="department.name" :value="department.id" /></el-select></el-form-item><el-form-item label="角色"><el-select v-model="form.role_ids" multiple class="full-width"><el-option v-for="role in roles.filter((item) => item.is_active)" :key="role.id" :label="role.name" :value="role.id" /></el-select></el-form-item><el-form-item v-if="dialogMode === 'edit'" label="账号状态"><el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" /></el-form-item></el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submit">保存</el-button></template>
  </el-dialog>

  <el-dialog v-model="resetDialogVisible" title="重置密码" width="420px"><p class="reset-hint">正在重置：{{ selectedUser?.display_name }}</p><el-form label-position="top"><el-form-item label="新密码"><el-input v-model="resetForm.password" type="password" show-password placeholder="至少 8 位" /></el-form-item></el-form><template #footer><el-button @click="resetDialogVisible = false">取消</el-button><el-button type="primary" @click="resetPassword">确认重置</el-button></template></el-dialog>
</template>

<style scoped>
.role-tag { margin: 2px 4px 2px 0; }
.muted, .reset-hint { color: #94a3b8; }
.full-width { width: 100%; }
</style>

