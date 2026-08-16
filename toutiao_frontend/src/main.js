import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './store'
import { useUserStore } from './store/user'
import { setAuthToken } from './api/request'

// 导入Vant组件库
import { 
  Button, 
  NavBar, 
  Tabbar, 
  TabbarItem, 
  Tab, 
  Tabs, 
  List, 
  PullRefresh, 
  Cell, 
  CellGroup,
  Grid,
  GridItem,
  Empty,
  Form,
  Field,
  Image,
  Toast,
  Icon,
  Popup
} from 'vant'

// 导入Vant样式
import 'vant/lib/index.css'

// 导入全局样式
import './style.css'

// 引入国际化
import { setupI18n } from './i18n'

const app = createApp(App)

// 设置i18n
const i18n = setupI18n()
app.use(i18n)

// 注册Vant组件
app.use(Button)
app.use(NavBar)
app.use(Tabbar)
app.use(TabbarItem)
app.use(Tab)
app.use(Tabs)
app.use(List)
app.use(PullRefresh)
app.use(Cell)
app.use(CellGroup)
app.use(Grid)
app.use(GridItem)
app.use(Empty)
app.use(Form)
app.use(Field)
app.use(Image)
app.use(Toast)
app.use(Icon)
app.use(Popup)

// 使用路由和状态管理
app.use(router)
app.use(pinia)

// 应用启动时将已持久化的 token 同步到请求拦截器（刷新页面后仍保持登录态）
const _userStore = useUserStore()
if (_userStore.token) {
  setAuthToken(_userStore.token)
}

// 统一处理 token 失效（401）：请求层派发事件，此处跳转登录页并清除登录态
window.addEventListener('auth:unauthorized', () => {
  const uStore = useUserStore()
  uStore.logout()
  if (router.currentRoute.value.path !== '/login') {
    router.push('/login')
  }
})

app.mount('#app')

// 初始化主题
import { useThemeStore } from './store/theme'
const themeStore = useThemeStore()
themeStore.initTheme()
