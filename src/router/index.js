import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'
import MyCatView from '../views/MyCatView.vue'
import ResumeView from '../views/ResumeView.vue'
import KomatsuWordlePage from '../views/KomatsuWordlePage.vue'
import MtgGameView from '../views/MtgGameView.vue'

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
      path: '/komatsu-le',
      name: 'KomatsuWordle',
      component: KomatsuWordlePage
    },
    {
      path: '/resume',
      name: 'resume',
      component: ResumeView
    },
    {
      path: '/mtg-game',
      name: 'mtg-game',
      component: MtgGameView
    },
    {
      path: '/sports',
      name: 'sports',
      component: () => import('@/views/SportsView.vue')
    }
  ]
})

export default router
