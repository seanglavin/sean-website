<template>
  <div class="max-w-2xl mx-auto">
    <div id="custom-carousel" class="relative" data-carousel="static">
      <!-- Carousel wrapper -->
      <div class="overflow-hidden relative h-56 rounded-lg sm:h-64 xl:h-80 2xl:h-96">
        <!-- Dynamically generate carousel items -->
        <div
          v-for="(image, index) in catImages"
          :key="index"
          class="hidden duration-700 ease-in-out"
          data-carousel-item
        >
          <span
            class="absolute top-1/2 left-1/2 text-2xl font-semibold text-white -translate-x-1/2 -translate-y-1/2 sm:text-3xl dark:text-gray-800"
          >
            {{ `Slide ${index + 1}` }}
          </span>
          <img
            :src="require(`@/assets/images/cats/${image}`)"
            class="block absolute top-1/2 left-1/2 w-full -translate-x-1/2 -translate-y-1/2"
            alt="..."
          />
        </div>
      </div>
      <!-- Slider indicators -->
      <div class="flex absolute bottom-5 left-1/2 z-30 space-x-3 -translate-x-1/2">
        <button
          v-for="(image, index) in catImages"
          :key="index"
          type="button"
          class="w-3 h-3 rounded-full"
          :aria-current="currentIndex === index"
          :aria-label="`Slide ${index + 1}`"
          :data-carousel-slide-to="index"
          @click="goToSlide(index)"
        ></button>
      </div>
      <!-- Slider controls -->
      <button
        type="button"
        class="flex absolute top-0 left-0 z-30 justify-center items-center px-4 h-full cursor-pointer group focus:outline-none"
        data-carousel-prev
        @click="prevSlide"
      >
        <!-- ... Previous button content remains unchanged ... -->
      </button>
      <button
        type="button"
        class="flex absolute top-0 right-0 z-30 justify-center items-center px-4 h-full cursor-pointer group focus:outline-none"
        data-carousel-next
        @click="nextSlide"
      >
        <!-- ... Next button content remains unchanged ... -->
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      catImages: [], // Array to hold the names of cat images
      currentIndex: 0 // Index of the current slide
    };
  },
  mounted() {
    // Fetch the list of cat images from the folder
    this.catImages = this.importAll(
      require.context('@/assets/images/cats', false, /\.(png|jpe?g|svg)$/)
    );
  },
  methods: {
    // Function to import all images from the given context
    importAll(context) {
      return context.keys().map(context);
    },
    // Function to navigate to a specific slide
    goToSlide(index) {
      this.currentIndex = index;
      // You can add additional logic here if needed
    },
    // Function to navigate to the previous slide
    prevSlide() {
      this.currentIndex = (this.currentIndex - 1 + this.catImages.length) % this.catImages.length;
      // You can add additional logic here if needed
    },
    // Function to navigate to the next slide
    nextSlide() {
      this.currentIndex = (this.currentIndex + 1) % this.catImages.length;
      // You can add additional logic here if needed
    }
  }
};
</script>

<style scoped>/* Add any styles specific to your carousel component */</style>
