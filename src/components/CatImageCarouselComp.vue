<template>
    <div class="gallery-container">
      <Carousel id="gallery" :items-to-show="1" :wrap-around="false" v-model="currentSlide">
        <Slide v-for="(image, index) in catImages" :key="index">
          <img :src="image" alt="Cat Image" class="gallery-image" />
        </Slide>
      </Carousel>
    </div>

    <div class="thumbnail-container">
      <Carousel id="thumbnails" :items-to-show="5" :wrap-around="false" v-model="currentSlide" ref="carousel">
        <Slide v-for="(image, index) in catImages" :key="index">
          <div class="thumbnail-item" @click="slideTo(index)">
            <img :src="image" alt="Cat Thumbnail" class="thumbnail-image" />
          </div>
        </Slide>
      </Carousel>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Carousel, Slide } from 'vue3-carousel'
import 'vue3-carousel/dist/carousel.css'

const currentSlide = ref(0)
const catImages = ref([])

function slideTo(index) {
  currentSlide.value = index
}

async function loadCatImages() {
  const imagesContext = import.meta.glob('@/assets/images/cats/*.jpg')
  const imagePaths = await Promise.all(
    Object.values(imagesContext).map(async (importImage) => {
      const { default: imagePath } = await importImage()
      return imagePath
    })
  )
  catImages.value = imagePaths
}

onMounted(() => loadCatImages())
</script>

<style scoped>
.gallery-container {
  @apply p-3 mb-2 w-full max-w-sm bg-black rounded-xl bg-opacity-20;
}
.gallery-image {
  @apply aspect-square object-cover rounded-xl w-full h-auto;
}
.thumbnail-container {
  @apply p-3 w-full max-w-sm bg-black rounded-xl bg-opacity-20;
}
.thumbnail-image {
  @apply aspect-square object-cover rounded-xl w-14 h-14;
}
</style>
