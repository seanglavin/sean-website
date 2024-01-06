import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'
import MyCatView from '../views/MyCatView.vue'
import ResumeView from '../views/ResumeView.vue'
import BlogView from '../views/BlogView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView
    },
    {
      path: '/mycat',
      name: 'mycat',
      component: MyCatView
    },
    {
      path: '/resume',
      name: 'resume',
      component: ResumeView
    },
    {
      path: '/blog',
      name: 'blog',
      component: BlogView
    }
  ]
})

export default router
