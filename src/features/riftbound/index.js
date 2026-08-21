import { panels } from './panels'

const RiftboundLayout = () => import('./components/RiftboundLayout.vue')

export const riftboundRoutes = [
  {
    path: '/riftbound',
    component: RiftboundLayout,
    children: panels.map((panel) => ({
      path: panel.path,
      name: `riftbound-${panel.id}`,
      component: panel.component,
      meta: panel.meta,
    })),
  },
]
