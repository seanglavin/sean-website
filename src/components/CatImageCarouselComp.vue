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

<script>
import { defineComponent } from 'vue'
import { Carousel, Slide } from 'vue3-carousel'
import 'vue3-carousel/dist/carousel.css'

export default defineComponent({
  name: 'Gallery',
  components: {
    Carousel,
    Slide,
  },
  data: () => ({
    currentSlide: 0,
    catImages: [], // Array to store cat images filenames
  }),
  created() {
    this.loadCatImages();
  },
  methods: {
    slideTo(index) {
      this.currentSlide = index;
    },
    async loadCatImages() {
      const imagesContext = import.meta.glob('@/assets/images/cats/*.jpg');
      const imagePaths = await Promise.all(
        Object.values(imagesContext).map(async (importImage) => {
          const { default: imagePath } = await importImage();
          return imagePath;
        })
      );
      this.catImages = imagePaths;
    },
  },
});
</script>

<style scoped>
.gallery-container {
  @apply p-3 mb-2;
  @apply bg-black rounded-xl bg-opacity-20;
  width: 325px;
  height: 325px;
}
.gallery-image {
  @apply aspect-square object-cover rounded-xl;
  width: 300px;
  height: 300px;
}
.thumbnail-container {
  @apply p-3;
  @apply bg-black rounded-xl bg-opacity-20;
  width: 325px;
}
.thumbnail-image {
  @apply aspect-square object-cover rounded-xl;
  width: 55px;
  height: 55px;
}
</style>
