<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Lock, Right, User } from '@element-plus/icons-vue'

import { getErrorMessage } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const form = reactive({ username: '', password: '' })
const errorMessage = ref('')

async function submit() {
  errorMessage.value = ''
  if (!form.username || !form.password) {
    errorMessage.value = '请输入用户名和密码'
    return
  }
  try {
    await auth.login(form.username, form.password)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    await router.replace(redirect)
  } catch (error) {
    errorMessage.value = getErrorMessage(error, '登录失败，请检查账号和密码')
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-panel">
      <div class="login-brand">
        <div class="login-mark">PM</div>
        <div>
          <strong>大数据项目管理平台</strong>
          <span>内部项目执行与管理</span>
        </div>
      </div>
      <div class="login-intro">
        <h1>登录工作台</h1>
        <p>查看项目状态、执行进度和管理信息</p>
      </div>
      <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />
      <el-form class="login-form" label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名">
          <el-input v-model="form.username" size="large" :prefix-icon="User" autocomplete="username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" size="large" :prefix-icon="Lock" type="password" show-password autocomplete="current-password" placeholder="请输入密码" />
        </el-form-item>
        <el-button class="login-submit" type="primary" size="large" :loading="auth.loading" :icon="Right" @click="submit">
          登录
        </el-button>
      </el-form>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background: #eef2f6;
}

.login-panel {
  width: min(440px, 100%);
  padding: 38px 40px 42px;
  border: 1px solid #e3e8ef;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 10px 30px rgb(15 23 42 / 8%);
}

.login-brand,
.login-intro {
  display: flex;
  align-items: center;
}

.login-brand {
  gap: 12px;
}

.login-mark {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 8px;
  color: #fff;
  background: #2f80ed;
  font-weight: 700;
}

.login-brand strong,
.login-brand span {
  display: block;
}

.login-brand strong {
  color: #17202a;
  font-size: 15px;
}

.login-brand span {
  margin-top: 3px;
  color: #64748b;
  font-size: 12px;
}

.login-intro {
  justify-content: space-between;
  margin: 42px 0 22px;
}

.login-intro h1 {
  margin: 0;
  color: #17202a;
  font-size: 24px;
}

.login-intro p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.login-form {
  margin-top: 18px;
}

.login-submit {
  width: 100%;
  margin-top: 8px;
}

@media (max-width: 520px) {
  .login-panel {
    padding: 28px 24px 32px;
  }

  .login-intro {
    display: block;
  }

  .login-intro p {
    margin-top: 8px;
  }
}
</style>

