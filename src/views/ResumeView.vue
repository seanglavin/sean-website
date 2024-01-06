<template>
  <div class="resume">
    <div class="min-h-screen flex flex-col items-center justify-top">
      <div class="text-center">
        <h1 class="text-xl text-accentColor underline font-extrabold sm:text-4xl p-5">Work Experience</h1>
      </div>
      <div class="card-container">
        <BasicCardComp v-for="(experience, index) in experiences" :key="index" :title="experience.title"
        :subtitle="experience.company" :body="experience.summary" />
      </div>
      <ButtonComp buttonText="Download PDF" />
    </div>
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
