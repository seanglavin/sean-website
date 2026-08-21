<template>
  <div class="riftbound">
    <h1 class="page-title">Riftbound</h1>
    <p class="page-intro">
      A card browser and Canadian price tracker for Riftbound: League of Legends.
    </p>
    <TabBar :tabs="tabs" aria-label="Riftbound sections" />
    <router-view />
  </div>
</template>

<script setup>
import TabBar from '@/components/ui/TabBar.vue'
import { panels } from '../panels'

const tabs = panels.map((panel) => ({
  id: panel.id,
  label: panel.label,
  to: { name: `riftbound-${panel.id}` },
}))
</script>

<style scoped>
.riftbound {
  @apply flex-col mx-3 pb-10
}
.page-title {
  @apply text-2xl text-accentColor underline font-extrabold sm:text-5xl p-5
}
.page-intro {
  @apply max-w-2xl mx-auto mb-4 sm:text-lg
}
</style>
