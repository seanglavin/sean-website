<template>
  <footer class="bot-bar">
    <ul class="bot-bar-links">
      <li class="footer-link" v-for="(link, index) in footerLinks" :key="index">
        <a :href="link.url" :target="link.target" :rel="link.rel">
          {{ link.text }}
        </a>
        <!-- add a | between each link -->
        <span v-if="index < footerLinks.length - 1" class="text-primaryLight"> | </span>
      </li>
    </ul>
  </footer>
</template>

<script setup>
const footerLinks = [
  { text: 'skglavin@gmail.com', url: 'mailto:skglavin@gmail.com' },
  { text: 'LinkedIn', url: 'https://www.linkedin.com/in/skglavin/', target: '_blank', rel: 'noopener' },
  { text: 'Github', url: 'https://github.com/seanglavin', target: '_blank', rel: 'noopener' },
]
</script>

<style scoped>
.bot-bar {
  @apply bg-secondaryBlueDark p-3 w-full
}
.bot-bar-links {
  @apply flex items-center justify-center list-none gap-2 m-0
}
.footer-link {
  @apply list-none text-accentColor2
}
</style>