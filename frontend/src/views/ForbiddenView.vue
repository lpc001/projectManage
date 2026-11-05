<template>
  <main class="forbidden-page">
    <el-result icon="warning" title="无权访问" sub-title="当前账号没有打开此页面所需的权限" />
  </main>
</template>

<style scoped>
.forbidden-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background: #f4f6f8;
}
</style>

