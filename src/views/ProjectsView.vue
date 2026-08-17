<template>
  <div class="projects">
    <h1 class="page-title">Projects</h1>
    <div class="card-container">
      <ProjectCardComp
        v-for="project in projects"
        :key="project.slug"
        :title="project.title"
        :category="project.category"
        :summary="project.summary"
        :link-to="project.route ?? `/projects/${project.slug}`"
      />
    </div>
  </div>
</template>

<script setup>
import ProjectCardComp from '@/components/ProjectCardComp.vue'
import projectsData from '@/assets/text/projects.json'

const projects = projectsData.projects
</script>

<style scoped>
.projects {
  @apply flex-col mx-3
}

.page-title {
  @apply text-2xl text-accentColor underline font-extrabold sm:text-5xl p-5
}
</style>
