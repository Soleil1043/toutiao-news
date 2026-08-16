import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: {
      title: '登录',
      keepAlive: false
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: {
      title: '注册',
      keepAlive: false
    }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: {
      title: '首页',
      keepAlive: true
    }
  },
  {
    path: '/news/detail/:id',
    name: 'NewsDetail',
    component: () => import('../views/NewsDetail.vue'),
    meta: {
      title: '新闻详情',
      keepAlive: false
    }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue'),
    meta: {
      title: '浏览历史',
      keepAlive: false
    }
  },
  {
    path: '/favorite',
    name: 'Favorite',
    component: () => import('../views/Favorite.vue'),
    meta: {
      title: '我的收藏',
      keepAlive: false
    }
  },
  {
    path: '/category',
    name: 'Category',
    component: () => import('../views/Category.vue'),
    meta: {
      title: '分类',
      keepAlive: true
    }
  },
  {
    path: '/aichat',
    name: 'AIChat',
    component: () => import('../views/AIChat.vue'),
    meta: {
      title: 'AI问答',
      keepAlive: true
    }
  },
  {
    path: '/my',
    name: 'My',
    component: () => import('../views/My.vue'),
    meta: {
      title: '我的',
      keepAlive: true
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: {
      title: '个人信息',
      keepAlive: false
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: {
      title: '设置',
      keepAlive: false
    }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 无需登录即可访问的公开页面
const publicPaths = ['/login', '/register', '/home', '/category']
function isPublic(path) {
  return publicPaths.includes(path) || path.startsWith('/news/detail')
}

// 全局前置守卫：设置标题 + 登录态鉴权
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '新闻资讯'

  const userStore = useUserStore()
  if (!isPublic(to.path) && !userStore.getLoginStatus) {
    // 未登录访问私有页面，重定向到登录页
    next('/login')
  } else {
    next()
  }
})

export default router
