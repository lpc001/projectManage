<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'

import { createSystemRole, listSystemPermissions, listSystemRoles, updateRolePermissions, updateSystemRole } from '@/api/systemAdmin'
import { getErrorMessage } from '@/api/http'
import type { DataScopeType, SystemPermission, SystemRole } from '@/types/system'

const roles = ref<SystemRole[]>([])
const permissions = ref<SystemPermission[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const selectedRole = ref<SystemRole | null>(null)
const form = reactive({ code: '', name: '', description: '', data_scope: 'member' as DataScopeType })
const selectedPermissionIds = ref<number[]>([])

async function load() {
  loading.value = true
  try {
    const [roleRows, permissionRows] = await Promise.all([listSystemRoles(), listSystemPermissions()])
    roles.value = roleRows
    permissions.value = permissionRows
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '角色配置加载失败'))
  } finally { loading.value = false }
}

function openCreate() {
  selectedRole.value = null
  Object.assign(form, { code: '', name: '', description: '', data_scope: 'member' })
  selectedPermissionIds.value = []
  dialogVisible.value = true
}

function editRole(role: SystemRole) {
  selectedRole.value = role
  Object.assign(form, { code: role.code, name: role.name, description: role.description || '', data_scope: role.data_scope })
  dialogVisible.value = true
}

async function submit() {
  try {
    if (selectedRole.value) await updateSystemRole(selectedRole.value.id, { name: form.name, description: form.description, data_scope: form.data_scope })
    else await createSystemRole(form)
    ElMessage.success('角色已保存')
    dialogVisible.value = false
    await load()
  } catch (error) { ElMessage.error(getErrorMessage(error, '角色保存失败')) }
}

async function savePermissions(role: SystemRole) {
  try {
    await updateRolePermissions(role.id, selectedPermissionIds.value)
    ElMessage.success('权限已更新')
  } catch (error) { ElMessage.error(getErrorMessage(error, '权限更新失败')) }
}

onMounted(load)
</script>

<template>
  <div class="page-header"><div><h1>角色管理</h1><p>配置角色权限和默认数据范围。</p></div><div class="page-actions"><el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button><el-button type="primary" :icon="Plus" @click="openCreate">新建角色</el-button></div></div>
  <el-card shadow="never">
    <el-table v-loading="loading" :data="roles" row-key="id">
      <el-table-column prop="name" label="角色名称" width="180" /><el-table-column prop="code" label="编码" width="220" /><el-table-column prop="data_scope" label="数据范围" width="160" /><el-table-column label="属性" width="120"><template #default="scope"><el-tag v-if="scope.row.is_builtin" type="info">内置</el-tag><el-tag v-else type="success">自定义</el-tag></template></el-table-column><el-table-column label="操作" width="120"><template #default="scope"><el-button text type="primary" @click="editRole(scope.row)">编辑</el-button></template></el-table-column>
    </el-table>
  </el-card>
  <el-dialog v-model="dialogVisible" :title="selectedRole ? '编辑角色' : '新建角色'" width="620px">
    <el-form label-position="top"><el-form-item label="角色编码"><el-input v-model="form.code" :disabled="Boolean(selectedRole)" /></el-form-item><el-form-item label="角色名称"><el-input v-model="form.name" /></el-form-item><el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item><el-form-item label="默认数据范围"><el-select v-model="form.data_scope" class="full-width"><el-option label="全部数据" value="all" /><el-option label="所属部门" value="department" /><el-option label="本人负责" value="owned" /><el-option label="本人参与" value="member" /><el-option label="自定义部门" value="custom_department" /></el-select></el-form-item><el-form-item v-if="selectedRole" label="权限"><el-checkbox-group v-model="selectedPermissionIds"><el-checkbox v-for="permission in permissions" :key="permission.id" :value="permission.id">{{ permission.name }} <span class="permission-code">{{ permission.code }}</span></el-checkbox></el-checkbox-group></el-form-item></el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submit">保存</el-button><el-button v-if="selectedRole" @click="savePermissions(selectedRole)">保存权限</el-button></template>
  </el-dialog>
</template>

<style scoped>
.full-width { width: 100%; }.permission-code { color: #94a3b8; font-size: 12px; }.el-checkbox { display: flex; width: 100%; margin: 0 0 8px; }
</style>

