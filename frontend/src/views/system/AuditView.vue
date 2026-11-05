<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

import { listAuditLogs } from '@/api/systemAdmin'
import { getErrorMessage } from '@/api/http'
import type { AuditLog } from '@/types/system'

const logs = ref<AuditLog[]>([])
const loading = ref(false)
async function load() { loading.value = true; try { logs.value = await listAuditLogs() } catch (error) { ElMessage.error(getErrorMessage(error, '审计记录加载失败')) } finally { loading.value = false } }
onMounted(load)
</script>

<template>
  <div class="page-header"><div><h1>操作审计</h1><p>查看系统管理和关键业务操作记录。</p></div><div class="page-actions"><el-button :icon="Refresh" :loading="loading" @click="load">刷新</el-button></div></div>
  <el-card shadow="never"><el-table v-loading="loading" :data="logs" row-key="id" empty-text="暂无审计记录"><el-table-column prop="created_at" label="时间" width="190" /><el-table-column prop="module" label="模块" width="120" /><el-table-column prop="action" label="操作" width="190" /><el-table-column prop="target_type" label="对象" width="120" /><el-table-column prop="result" label="结果" width="90" /><el-table-column prop="summary" label="摘要" min-width="260" show-overflow-tooltip /></el-table></el-card>
</template>

