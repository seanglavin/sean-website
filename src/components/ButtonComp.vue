<template>
  <button class="button" @click="handleClick">
    <slot>{{ buttonText }}</slot>
  </button>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  buttonText: String,
  routePath: String,
  downloadPdf: { type: Boolean, default: false },
})

const router = useRouter()

function handleClick() {
  if (props.routePath) {
    router.push(props.routePath)
  } else if (props.downloadPdf) {
    downloadResumePDF()
  }
}

async function downloadResumePDF() {
  try {
    const _filename = 'SeanGlavinResume.pdf'
    const pdfPath = import.meta.env.BASE_URL + _filename

    const link = document.createElement('a')
    link.href = pdfPath
    link.download = 'downloaded-file-' + _filename
    link.click()

    if (document.body.contains(link)) {
      document.body.removeChild(link)
    }

    window.URL.revokeObjectURL(link.href)
  } catch (error) {
    console.error('Error downloading PDF:', error)
  }
}
</script>

<style scoped>
.button {
  @apply block m-3 w-full font-bold px-12 py-3 bg-accentColor rounded cursor-pointer hover:bg-accentColor2
}
</style>
