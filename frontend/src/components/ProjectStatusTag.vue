<script setup lang="ts">
import { computed } from 'vue'
import { ElTag } from 'element-plus'

import type { ProjectLifecycleStatus } from '@/types/project'

const props = defineProps<{ status: ProjectLifecycleStatus }>()

const statusMeta = computed(() => {
  const values: Record<ProjectLifecycleStatus, { label: string; type: 'info' | 'success' | 'warning' | 'danger' }> = {
    planning: { label: '筹备中', type: 'info' },
    active: { label: '执行中', type: 'success' },
    completed: { label: '已完成', type: 'success' },
    paused: { label: '已暂停', type: 'warning' },
    archived: { label: '已归档', type: 'info' },
  }
  return values[props.status]
})
</script>

<template>
  <ElTag :type="statusMeta.type" effect="light">{{ statusMeta.label }}</ElTag>
</template>

