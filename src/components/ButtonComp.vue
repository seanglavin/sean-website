<template>
  <button
    class="block w-full rounded bg-accentColor px-12 py-3 text-sm font-bold shadow hover:bg-accentColor2 focus:outline-none focus:ring sm:w-auto"
    @click="handleClick">
    <slot>{{ buttonText }}</slot>
  </button>
</template>

<script>
export default {
  props: {
    buttonText: String,
    routePath: String // Specify the route if you want the button to navigate to a page
  },
  methods: {
    handleClick() {
      if (this.routePath) {
        this.routeTo()
      } else {
        this.downloadResumePDF()
      }
    },
    routeTo() {
      this.$router.push(this.routePath) // Route to the specified page
    },
    async downloadResumePDF() {
      try {
        const _filename = 'SeanGlavinResume.pdf'
        const pdfPath = process.env.BASE_URL + _filename

        const link = document.createElement('a')

        link.href = pdfPath

        link.download = 'downloaded-file-' + _filename

        link.click()

        window.URL.revokeObjectURL(link.href)
        // Remove the anchor element from the document
        document.body.removeChild(link)
      } catch (error) {
        console.error('Error downloading PDF:', error)
      }
    }
  }
}
</script>

<style scoped>
.button {
  @apply inline-block px-4 py-2 bg-red-500 text-white rounded cursor-pointer transition duration-300 ease-in-out
}

.button:hover {
  @apply bg-red-600;
}
</style>
