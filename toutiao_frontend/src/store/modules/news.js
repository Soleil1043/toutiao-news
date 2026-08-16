import { defineStore } from 'pinia'
import request from '../../api/request'

// 分类栏的“更多”虚拟入口（非真实分类，仅 UI 用途）
const MORE_CATEGORY = { id: 10, name: '更多' }

// 接口失败时的兜底分类，避免分类栏空白
const FALLBACK_CATEGORIES = [
  { id: 1, name: '头条' },
  { id: 2, name: '社会' },
  { id: 3, name: '国内' },
  { id: 4, name: '国际' },
  { id: 5, name: '娱乐' },
  { id: 6, name: '体育' },
  { id: 7, name: '科技' },
  { id: 8, name: '财经' }
]

export const useNewsStore = defineStore('news', {
  state: () => ({
    newsList: [],
    newsDetail: {},
    categories: [],
    currentCategory: 1,
    loading: false,
    refreshing: false,
    finished: false,
    categoriesLoading: false,
    detailLoading: false,
    detailError: false
  }),
  
  actions: {
    // 获取新闻分类
    async getCategories() {
      if (this.categoriesLoading) return;
      
      this.categoriesLoading = true;
      
      try {
        // 调用API获取分类列表
        const response = await request.get('/api/news/categories');
        
        if (response.data && response.data.code === 200) {
          // 设置分类数据
          this.categories = [...response.data.data, MORE_CATEGORY];
          
          // 如果没有设置当前分类，则设置为第一个分类
          if (!this.currentCategory && this.categories.length > 0) {
            this.currentCategory = this.categories[0].id;
          }
        }
      } catch (error) {
        console.error('获取新闻分类失败:', error);
        // 接口失败，使用兜底分类，避免分类栏空白
        this.categories = FALLBACK_CATEGORIES;
      } finally {
        this.categoriesLoading = false;
      }
    },
    
    // 切换新闻分类
    changeCategory(categoryId) {
      if (this.currentCategory !== categoryId) {
        this.currentCategory = categoryId
        this.newsList = []
        this.finished = false
        this.getNewsList(true)
      }
    },
    
    // 获取新闻列表
    async getNewsList(isRefresh = false) {
      if (isRefresh) {
        this.refreshing = true
        this.newsList = []
        this.finished = false
      }
      
      this.loading = true
      
      try {
        const params = {
          categoryId: this.currentCategory,
          page: isRefresh ? 1 : Math.ceil(this.newsList.length / 10) + 1,
          pageSize: 10
        }
        
        const response = await request.get('/api/news/list', { params });
        
        if (response.data && response.data.code === 200) {
          const newsData = response.data.data.list;
          
          // 更新新闻列表
          this.newsList = isRefresh ? newsData : [...this.newsList, ...newsData];
          
          // 判断是否加载完成
          if (newsData.length < params.pageSize) {
            this.finished = true;
          }
        }

      } catch (error) {
        console.error('获取新闻列表失败:', error)
      } finally {
        this.loading = false
        this.refreshing = false
      }
    },
    
    // 获取新闻详情
    async getNewsDetail(id) {
      this.detailLoading = true;
      this.detailError = false;
      
      try {
        const response = await request.get(`/api/news/detail?id=${id}`);
        
        if (response.data && response.data.code === 200) {
          // 设置新闻详情数据
          this.newsDetail = response.data.data;
          return;
        } else {
          console.error('获取新闻详情失败: 接口返回错误');
          this.detailError = true;
        }
      } catch (error) {
        console.error('获取新闻详情失败:', error);
        this.detailError = true;
      } finally {
        this.detailLoading = false;
      }
    },
    
    // 获取分类名称
    getCategoryName(categoryId) {
      const category = this.categories.find(item => item.id === categoryId)
      return category ? category.name : '未知'
    }
  }
})
