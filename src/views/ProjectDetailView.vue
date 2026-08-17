<template>
  <div class="project-detail" v-if="project">
    <h1 class="page-title">{{ project.title }}</h1>
    <div class="text-container">
      <p class="body-text">{{ project.description }}</p>
      <a
        v-if="project.externalUrl"
        :href="project.externalUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="project-link"
      >View project</a>
    </div>
  </div>
  <div class="project-detail" v-else>
    <h1 class="page-title">Project not found</h1>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import projectsData from '@/assets/text/projects.json'

const route = useRoute()
const project = computed(() =>
  projectsData.projects.find((p) => p.slug === route.params.slug)
)
</script>

<style scoped>
.project-detail {
  @apply flex-col mx-3
}

.page-title {
  @apply text-2xl text-accentColor underline font-extrabold sm:text-5xl p-5
}

.text-container {
  @apply max-w-xl text-center mx-auto p-3 mt-3;
  @apply bg-black rounded-xl bg-opacity-20;
}

.body-text {
  @apply sm:text-xl/relaxed lg:text-2xl/relaxed
}

.project-link {
  @apply inline-block mt-4 font-bold text-accentColor hover:text-accentColor2
}
</style>
