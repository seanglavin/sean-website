<template>
  <div>
    <Carousel id="gallery" :items-to-show="1" :wrap-around="false" v-model="currentSlide">
      <Slide v-for="(image, index) in catImages" :key="index">
        <img :src="image" alt="Cat Image" />
      </Slide>
    </Carousel>

    <Carousel
      id="thumbnails"
      :items-to-show="4"
      :wrap-around="true"
      v-model="currentSlide"
      ref="carousel"
    >
      <Slide v-for="(image, index) in catImages" :key="index">
        <div class="thumbnail-item" @click="slideTo(index)">
          <img :src="image" alt="Cat Thumbnail" />
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
