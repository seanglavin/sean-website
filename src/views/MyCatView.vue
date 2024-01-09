<template>
  <div class="my-cat">
    <h1 class="page-title">This is Girl!</h1>
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
.my-cat {
  @apply flex flex-col px-3;
  align-items: center;
}
.page-title {
  @apply text-2xl text-accentColor underline font-extrabold sm:text-5xl p-5
}
.image-carousel-container {
  align-items: center;
}
</style>
