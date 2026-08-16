import { defineStore } from 'pinia';
import request from '../api/request';
import { setAuthToken, clearAuthToken } from '../api/request';

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null,
    token: '',
    isLogin: false,
    userBio: '这是我的个人简介'
  }),
  
  getters: {
    getUserInfo: (state) => state.userInfo,
    getToken: (state) => state.token,
    getLoginStatus: (state) => state.isLogin,
    getUserBio: (state) => state.userInfo?.bio || state.userBio
  },
  
  actions: {
    async login(userData) {
      try {
        const response = await request.post('/api/users/login', {
          username: userData.username,
          password: userData.password
        });
        
        if (response.data && response.data.code === 200) {
          const userInfo = response.data.data.userInfo;
          const token = response.data.data.token;
          
          this.userInfo = userInfo;
          this.token = token;
          this.isLogin = true;
          // 同步 token 到请求拦截器
          setAuthToken(token);
          
          return {
            success: true,
            message: '登录成功'
          };
        } else {
          return {
            success: false,
            message: response.data.message || '登录失败'
          };
        }
      } catch (error) {
        console.error('登录请求失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '登录请求失败，请稍后再试'
        };
      }
    },
    
    async register(userData) {
      try {
        const response = await request.post('/api/users/register', {
          username: userData.username,
          password: userData.password
        });
        
        if (response.data && response.data.code === 200) {
          const userInfo = response.data.data.userInfo;
          const token = response.data.data.token;
          
          this.userInfo = userInfo;
          this.token = token;
          this.isLogin = true;
          setAuthToken(token);
          
          return {
            success: true,
            message: '注册成功'
          };
        } else {
          return {
            success: false,
            message: response.data.message || '注册失败'
          };
        }
      } catch (error) {
        console.error('注册请求失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '注册请求失败，请稍后再试'
        };
      }
    },
    
    logout() {
      clearAuthToken();
      this.userInfo = null;
      this.token = '';
      this.isLogin = false;
    },
    
    async getUserInfoDetail() {
      try {
        if (!this.token) {
          return {
            success: false,
            message: '未登录'
          };
        }
        
        const response = await request.get('/api/users/info');
        
        if (response.data && response.data.code === 200) {
          this.userInfo = response.data.data;
          
          return {
            success: true,
            message: '获取用户信息成功',
            data: response.data.data
          };
        } else {
          return {
            success: false,
            message: response.data.message || '获取用户信息失败'
          };
        }
      } catch (error) {
        console.error('获取用户信息请求失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '获取用户信息请求失败，请稍后再试'
        };
      }
    },
    
    async updateUserInfo(data) {
      try {
        if (!this.token) {
          return {
            success: false,
            message: '未登录'
          };
        }

        const response = await request.put('/api/users/update', data);
        
        if (response.data && response.data.code === 200) {
          // 用后端返回的最新用户信息整体刷新，避免本地状态不同步
          this.userInfo = response.data.data;
          
          return {
            success: true,
            message: '更新成功'
          };
        } else {
          return {
            success: false,
            message: response.data.message || '更新失败'
          };
        }
      } catch (error) {
        console.error('更新用户信息请求失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '更新请求失败，请稍后再试'
        };
      }
    },
    
    async updatePassword(oldPassword, newPassword) {
      try {
        if (!this.token) {
          return {
            success: false,
            message: '未登录'
          };
        }
        
        const response = await request.put('/api/users/password', { 
          oldPassword,
          newPassword 
        });
        
        if (response.data && response.data.code === 200) {
          return {
            success: true,
            message: '密码修改成功'
          };
        } else {
          return {
            success: false,
            message: response.data.message || '密码修改失败'
          };
        }
      } catch (error) {
        console.error('修改密码请求失败:', error);
        return {
          success: false,
          message: error.response?.data?.message || '修改密码请求失败，请稍后再试'
        };
      }
    }
  },
  
  // 持久化配置（pinia-plugin-persistedstate v4 语法）
  // token 存于 sessionStorage：刷新页面仍保持登录，关闭标签页即清除，避免明文常驻 localStorage
  persist: {
    key: 'user-store',
    storage: sessionStorage,
    pick: ['userInfo', 'isLogin', 'token']
  }
});
