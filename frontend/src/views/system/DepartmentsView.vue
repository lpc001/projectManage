<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'

import { createSystemDepartment, listSystemDepartments, updateSystemDepartment } from '@/api/systemAdmin'
import { getErrorMessage } from '@/api/http'
import type { SystemDepartment } from '@/types/system'

const departments = ref<SystemDepartment[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ name: '', code: '', parent_id: undefined as number | undefined })
async function load() { loading.value = true; try { departments.value = await listSystemDepartments() } catch (error) { ElMessage.error(getErrorMessage(error, '部门加载失败')) } finally { loading.value = false } }
function openCreate() { Object.assign(form, { name: '', code: '', parent_id: undefined }); dialogVisible.value = true }
async function submit() { try { await createSystemDepartment({ ...form, parent_id: form.parent_id }); ElMessage.success('部门创建成功'); dialogVisible.value = false; await load() } catch (error) { ElMessage.error(getErrorMessage(error, '部门创建失败')) } }
async function toggle(department: SystemDepartment) { try { await updateSystemDepartment(department.id, { is_active: !department.is_active }); ElMessage.success('部门状态已更新'); await load() } catch (error) { ElMessage.error(getErrorMessage(error, '部门状态更新失败')) } }
onMounted(load)
</script>

<template>
  <div class="page-header"><div><h1>部门管理</h1><p>维护组织结构和用户主部门。</p></div><div class="page-actions"><el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button><el-button type="primary" :icon="Plus" @click="openCreate">新建部门</el-button></div></div>
  <el-card shadow="never"><el-table v-loading="loading" :data="departments" row-key="id"><el-table-column prop="name" label="部门名称" min-width="200" /><el-table-column prop="code" label="编码" width="200" /><el-table-column label="状态" width="100"><template #default="scope"><el-tag :type="scope.row.is_active ? 'success' : 'info'">{{ scope.row.is_active ? '启用' : '停用' }}</el-tag></template></el-table-column><el-table-column label="操作" width="100"><template #default="scope"><el-button text type="primary" @click="toggle(scope.row)">{{ scope.row.is_active ? '停用' : '启用' }}</el-button></template></el-table-column></el-table></el-card>
  <el-dialog v-model="dialogVisible" title="新建部门" width="460px"><el-form label-position="top"><el-form-item label="部门名称"><el-input v-model="form.name" /></el-form-item><el-form-item label="部门编码"><el-input v-model="form.code" /></el-form-item></el-form><template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submit">创建</el-button></template></el-dialog>
</template>

