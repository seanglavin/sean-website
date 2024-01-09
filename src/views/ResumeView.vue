<template>
  <div class="resume">
      <h1 class="page-title">Work Experience</h1>
      <div class="card-container">
        <BasicCardComp v-for="(experience, index) in experiences" :key="index" :title="experience.title"
        :subtitle="experience.company" :body="experience.summary" />
      </div>
      <ButtonComp class="button" buttonText="Download PDF" />
    <!-- </div> -->
  </div>
</template>

<script>
import ButtonComp from '@/components/ButtonComp.vue'
import BasicCardComp from '@/components/BasicCardComp.vue'
import jsonData from '@/assets/text/work-experience-summaries.json'

export default {
  components: {
    ButtonComp,
    BasicCardComp
  },
  data() {
    return {
      experiences: jsonData.experience
    }
  }
}
</script>

<style scoped>

.resume {
  @apply flex-col mx-3
}

/* page title css */
.page-title {
  @apply text-2xl text-accentColor underline font-extrabold sm:text-5xl p-5
}

.button {
  @apply mt-6 sm:w-auto mx-auto
}
</style>