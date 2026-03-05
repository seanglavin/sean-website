<template>
  <div class="my-cat">
    <h1 class="page-title">This is Girl!</h1>
    <div class="image-carousel-container">
      <CatImageCarouselComp />
    </div>
  </div>
</template>

<script setup>
import CatImageCarouselComp from '@/components/CatImageCarouselComp.vue'
</script>

<style scoped>
.my-cat {
  @apply flex flex-col items-center px-3;
}
.page-title {
  @apply text-2xl text-accentColor underline font-extrabold sm:text-5xl p-5
}
.image-carousel-container {
  @apply flex flex-col items-center justify-center;
}
</style>
