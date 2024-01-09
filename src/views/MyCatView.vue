<template>
  <div class="my-cat">
    <h1>This is a page for my cat, Girl!</h1>
    <div class="image-carousel-container">
      <CatImageCarouselComp />
    </div>
  </div>
</template>

<script>
import CatImageCarouselComp from '@/components/CatImageCarouselComp.vue'

export default {
  components: {
    CatImageCarouselComp
  }
}
</script>

<style scoped>
/* Add any styles specific to your view */
</style>
