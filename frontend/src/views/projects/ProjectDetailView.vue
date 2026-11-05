<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Link, Warning } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'

import { archiveProject, fetchProject } from '@/api/projects'
import { getErrorMessage } from '@/api/http'
import ProjectStatusTag from '@/components/ProjectStatusTag.vue'
import { useAuthStore } from '@/stores/auth'
import type { ProjectDetail } from '@/types/project'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const project = ref<ProjectDetail | null>(null)
const loading = ref(false)
const canEdit = computed(() => auth.hasPermission('project:update'))

async function loadProject() {
  loading.value = true
  try {
    project.value = await fetchProject(Number(route.params.id), auth.hasPermission('project:archive'))
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '项目加载失败'))
  } finally {
    loading.value = false
  }
}

async function archive() {
  if (!project.value) return
  try {
    await ElMessageBox.confirm(`确认归档项目“${project.value.name}”吗？归档后默认列表不再展示。`, '归档项目', {
      type: 'warning',
      confirmButtonText: '确认归档',
      cancelButtonText: '取消',
    })
    project.value = await archiveProject(project.value.id)
    ElMessage.success('项目已归档')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(getErrorMessage(error, '归档失败'))
  }
}

onMounted(loadProject)
</script>

<template>
  <div v-loading="loading">
    <div v-if="project" class="page-header">
      <div>
        <div class="breadcrumb-link" @click="router.push('/projects')"><el-icon><ArrowLeft /></el-icon>返回项目台账</div>
        <div class="title-row"><h1>{{ project.name }}</h1><ProjectStatusTag :status="project.lifecycle_status" /></div>
        <p>{{ project.code }} · {{ project.client_name || '未填写客户' }}</p>
      </div>
      <div class="page-actions">
        <el-button v-if="canEdit && !project.is_archived" :icon="Edit" @click="router.push(`/projects/${project.id}/edit`)">编辑</el-button>
        <el-button v-if="auth.hasPermission('project:archive') && !project.is_archived" type="warning" :icon="Warning" @click="archive">归档</el-button>
      </div>
    </div>

    <el-skeleton v-if="loading && !project" :rows="8" animated />
    <el-empty v-else-if="!project" description="项目不存在或无权查看" />
    <template v-else>
      <div class="detail-grid">
        <el-card shadow="never">
          <template #header><strong>项目基线</strong></template>
          <dl class="detail-list">
            <div><dt>项目经理</dt><dd>{{ project.project_manager_name }}</dd></div>
            <div><dt>执行地区</dt><dd>{{ project.region || '未填写' }}</dd></div>
            <div><dt>计划开始</dt><dd>{{ project.planned_start_date }}</dd></div>
            <div><dt>计划结束</dt><dd>{{ project.planned_end_date }}</dd></div>
            <div class="span-2"><dt>项目说明</dt><dd>{{ project.description || '未填写' }}</dd></div>
          </dl>
        </el-card>
        <el-card shadow="never">
          <template #header><strong>材料链接</strong></template>
          <div v-if="project.seafile_url" class="link-box"><el-icon><Link /></el-icon><a :href="project.seafile_url" target="_blank" rel="noreferrer">打开 Seafile 项目材料</a></div>
          <el-empty v-else :image-size="56" description="暂未配置 Seafile 链接" />
        </el-card>
      </div>
      <el-card shadow="never" class="stage-card">
        <template #header><div class="section-heading"><strong>阶段与模块</strong><el-tag type="info">下一阶段启用</el-tag></div></template>
        <el-empty :image-size="72" description="项目分项将在下一阶段维护" />
      </el-card>
    </template>
  </div>
</template>

<style scoped>
.breadcrumb-link { display: inline-flex; align-items: center; gap: 4px; margin-bottom: 10px; color: #3c82d6; cursor: pointer; font-size: 13px; }
.title-row { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
.title-row h1 { margin: 0; }
.detail-grid { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(280px, 1fr); gap: 20px; }
.detail-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px 24px; margin: 0; }
.detail-list > div { min-width: 0; }
.detail-list .span-2 { grid-column: span 2; }
dt { color: #64748b; font-size: 12px; }
dd { margin: 5px 0 0; color: #1f2937; line-height: 1.6; word-break: break-word; }
.link-box { display: flex; align-items: center; gap: 8px; padding: 16px; border: 1px solid #d9e6f5; background: #f6faff; color: #2f74c0; }
.link-box a { color: inherit; }
.stage-card { margin-top: 20px; }
.section-heading { display: flex; align-items: center; justify-content: space-between; }
@media (max-width: 800px) { .detail-grid { grid-template-columns: 1fr; } }
@media (max-width: 520px) { .detail-list { grid-template-columns: 1fr; } .detail-list .span-2 { grid-column: auto; } }
</style>

