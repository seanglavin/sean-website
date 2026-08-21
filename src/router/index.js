import { createRouter, createWebHistory } from 'vue-router'
import projectsData from '../assets/text/projects.json'
import { riftboundRoutes } from '../features/riftbound'

const HomeView = () => import('../views/HomeView.vue')
const AboutView = () => import('../views/AboutView.vue')
const MyCatView = () => import('../views/MyCatView.vue')
const ResumeView = () => import('../views/ResumeView.vue')
const MtgGameView = () => import('../views/MtgGameView.vue')
const ProjectsView = () => import('../views/ProjectsView.vue')
const ProjectDetailView = () => import('../views/ProjectDetailView.vue')

const SITE_URL = 'https://skglavin.com'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'Sean Glavin',
        description: "Sean Glavin's personal website — background, work experience, and side projects.",
      }
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
      meta: {
        title: 'About | Sean Glavin',
        description: 'A bit about Sean Glavin — background and interests.',
      }
    },
    {
      path: '/mycat',
      name: 'mycat',
      component: MyCatView,
      meta: {
        title: 'My Cat | Sean Glavin',
        description: "Photos of Sean Glavin's cat, Girl.",
      }
    },
    {
      path: '/resume',
      name: 'resume',
      component: ResumeView,
      meta: {
        title: 'Resume | Sean Glavin',
        description: "Sean Glavin's work experience and resume.",
      }
    },
    {
      path: '/mtg-game',
      name: 'mtg-game',
      component: MtgGameView,
      meta: {
        title: 'MTG Art Game | Sean Glavin',
        description: 'A Magic: The Gathering card-guessing game, currently being redesigned.',
      }
    },
    {
      path: '/projects',
      name: 'projects',
      component: ProjectsView,
      meta: {
        title: 'Projects | Sean Glavin',
        description: 'Personal and professional projects by Sean Glavin.',
      }
    },
    ...riftboundRoutes,
    {
      path: '/projects/:slug',
      name: 'project-detail',
      component: ProjectDetailView,
      beforeEnter: (to) => {
        const project = projectsData.projects.find((p) => p.slug === to.params.slug)
        if (project?.route) return project.route
      },
    },
  ]
})

router.afterEach((to) => {
  const meta = resolveMeta(to)
  document.title = meta.title

  const url = SITE_URL + to.path
  setMetaContent('name', 'description', meta.description)
  setMetaContent('property', 'og:title', meta.title)
  setMetaContent('property', 'og:description', meta.description)
  setMetaContent('property', 'og:url', url)
  setLinkHref('canonical', url)
})

function resolveMeta(to) {
  if (to.name === 'project-detail') {
    const project = projectsData.projects.find((p) => p.slug === to.params.slug)
    if (project) {
      return {
        title: `${project.title} | Sean Glavin`,
        description: project.summary,
      }
    }
  }
  return {
    title: to.meta.title ?? 'Sean Glavin',
    description: to.meta.description ?? '',
  }
}

function setMetaContent(attr, key, content) {
  const el = document.querySelector(`meta[${attr}="${key}"]`)
  if (el) el.setAttribute('content', content)
}

function setLinkHref(rel, href) {
  const el = document.querySelector(`link[rel="${rel}"]`)
  if (el) el.setAttribute('href', href)
}

export default router
