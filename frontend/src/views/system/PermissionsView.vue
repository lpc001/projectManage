<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

import { listSystemPermissions } from '@/api/systemAdmin'
import { getErrorMessage } from '@/api/http'
import type { SystemPermission } from '@/types/system'

const permissions = ref<SystemPermission[]>([])
const loading = ref(false)
async function load() { loading.value = true; try { permissions.value = await listSystemPermissions() } catch (error) { ElMessage.error(getErrorMessage(error, '权限目录加载失败')) } finally { loading.value = false } }
onMounted(load)
</script>

<template>
  <div class="page-header"><div><h1>权限目录</h1><p>查看菜单、操作和 API 权限编码，内置编码由系统维护。</p></div><div class="page-actions"><el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button></div></div>
  <el-card shadow="never"><el-table v-loading="loading" :data="permissions" row-key="id"><el-table-column prop="name" label="名称" min-width="180" /><el-table-column prop="code" label="编码" min-width="280" /><el-table-column prop="permission_type" label="类型" width="100" /><el-table-column prop="route_path" label="路由" width="180" /><el-table-column prop="api_path" label="API" min-width="260" /><el-table-column label="状态" width="100"><template #default="scope"><el-tag :type="scope.row.is_active ? 'success' : 'info'">{{ scope.row.is_active ? '启用' : '停用' }}</el-tag></template></el-table-column></el-table></el-card>
</template>

