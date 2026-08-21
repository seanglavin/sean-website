export const panels = [
  {
    id: 'cards',
    path: '',
    label: 'Cards',
    component: () => import('./panels/CardBrowserPanel.vue'),
    meta: {
      title: 'Riftbound Cards | Sean Glavin',
      description: 'Search and filter the Riftbound: League of Legends card catalogue.',
    },
  },
  {
    id: 'prices',
    path: 'prices',
    label: 'Prices',
    component: () => import('./panels/PricesPanel.vue'),
    meta: {
      title: 'Riftbound Prices | Sean Glavin',
      description: 'Compare Riftbound single card prices and availability across Canadian retailers.',
    },
  },
  {
    id: 'collection',
    path: 'collection',
    label: 'Collection',
    component: () => import('./panels/CollectionPanel.vue'),
    meta: {
      title: 'Riftbound Collection | Sean Glavin',
      description: 'Track owned and wanted Riftbound cards with current Canadian prices.',
    },
  },
]
