<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
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

const permissionGroups = computed(() => {
  const menuById = new Map(permissions.value.filter((item) => item.permission_type === 'menu').map((item) => [item.id, item]))
  const menuByCode = new Map(permissions.value.filter((item) => item.permission_type === 'menu').map((item) => [item.code, item]))
  const groups = new Map<string, { key: string; label: string; sort: number; items: SystemPermission[] }>()
  for (const permission of permissions.value) {
    const derivedCode = `${permission.code.split(':').slice(0, 2).join(':')}:menu`
    const parent = permission.permission_type === 'menu' ? permission : (permission.parent_id ? menuById.get(permission.parent_id) : menuByCode.get(derivedCode))
    const key = parent?.code || derivedCode
    const group = groups.get(key) || { key, label: parent?.name || key, sort: parent?.sort_order || permission.sort_order, items: [] }
    group.items.push(permission)
    groups.set(key, group)
  }
  return Array.from(groups.values()).sort((a, b) => a.sort - b.sort)
})

const permissionTypeLabel = (type: SystemPermission['permission_type']) => ({ menu: '菜单', action: '操作', api: 'API' })[type]
const scopeLabel = (scope: DataScopeType) => ({ all: '全部数据', department: '所属部门', owned: '本人负责', member: '本人参与', custom_department: '自定义部门' })[scope]

async function load() {
  loading.value = true
  try {
    const [roleRows, permissionRows] = await Promise.all([listSystemRoles(), listSystemPermissions()])
    roles.value = roleRows
    permissions.value = permissionRows
  } catch (error) { ElMessage.error(getErrorMessage(error, '角色配置加载失败')) } finally { loading.value = false }
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
  selectedPermissionIds.value = [...role.permission_ids]
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
    await load()
  } catch (error) { ElMessage.error(getErrorMessage(error, '权限更新失败')) }
}

onMounted(load)
</script>

<template>
  <div class="page-header"><div><h1>角色管理</h1><p>按菜单和功能分类配置角色权限，数据范围单独管理。</p></div><div class="page-actions"><el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button><el-button type="primary" :icon="Plus" @click="openCreate">新建角色</el-button></div></div>
  <el-card shadow="never">
    <el-table v-loading="loading" :data="roles" row-key="id">
      <el-table-column prop="name" label="角色名称" width="180" /><el-table-column prop="code" label="编码" width="220" /><el-table-column label="数据范围" width="160"><template #default="scope">{{ scopeLabel(scope.row.data_scope) }}</template></el-table-column><el-table-column label="属性" width="120"><template #default="scope"><el-tag v-if="scope.row.is_builtin" type="info">内置</el-tag><el-tag v-else type="success">自定义</el-tag></template></el-table-column><el-table-column label="操作" width="120"><template #default="scope"><el-button text type="primary" @click="editRole(scope.row)">编辑</el-button></template></el-table-column>
    </el-table>
  </el-card>
  <el-dialog v-model="dialogVisible" :title="selectedRole ? '编辑角色' : '新建角色'" width="760px">
    <el-form label-position="top"><el-form-item label="角色编码"><el-input v-model="form.code" :disabled="Boolean(selectedRole)" /></el-form-item><el-form-item label="角色名称"><el-input v-model="form.name" /></el-form-item><el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item><el-form-item label="默认数据范围"><el-select v-model="form.data_scope" class="full-width"><el-option v-for="(label, value) in { all: '全部数据', department: '所属部门', owned: '本人负责', member: '本人参与', custom_department: '自定义部门' }" :key="value" :label="label" :value="value" /></el-select></el-form-item>
      <el-form-item v-if="selectedRole" label="权限配置"><el-alert title="按菜单分组展示，菜单、操作和 API 权限分别标注" type="info" :closable="false" class="permission-help" /><div class="permission-groups"><section v-for="group in permissionGroups" :key="group.key" class="permission-group"><div class="permission-group-title">{{ group.label }}</div><el-checkbox-group v-model="selectedPermissionIds"><el-checkbox v-for="permission in group.items" :key="permission.id" :value="permission.id"><span class="permission-name">{{ permission.name }}</span><el-tag size="small" effect="plain">{{ permissionTypeLabel(permission.permission_type) }}</el-tag><span class="permission-code">{{ permission.code }}</span></el-checkbox></el-checkbox-group></section></div></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submit">保存角色</el-button><el-button v-if="selectedRole" type="success" @click="savePermissions(selectedRole)">保存权限</el-button></template>
  </el-dialog>
</template>

<style scoped>
.full-width { width: 100%; }
.permission-help { margin-bottom: 12px; }
.permission-groups { display: grid; gap: 14px; max-height: 420px; overflow: auto; padding-right: 4px; }
.permission-group { border: 1px solid #e4e9ef; border-radius: 6px; padding: 12px 14px 8px; }
.permission-group-title { margin-bottom: 10px; color: #1f2937; font-size: 14px; font-weight: 700; }
.el-checkbox { display: flex; width: 100%; align-items: center; margin: 0 0 9px; }
.permission-name { min-width: 110px; }
.permission-code { margin-left: 8px; color: #94a3b8; font-size: 12px; }
</style>

