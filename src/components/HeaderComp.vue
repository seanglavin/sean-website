<template>
  <header class="top-bar">
    <nav class="top-bar-nav">
      <!-- Add nav icons later! -->
      <router-link class="nav-bar-link"
        v-for="(link, index) in headerLinks" :key="index" :to="link.to">
        <span>{{ link.text }}</span>
        <!-- adds a | between each link -->
        <span v-if="index < headerLinks.length - 1" class="text-primaryLight"> | </span>
      </router-link>
    </nav>
  </header>
</template>

<script>
export default {
  data() {
    return {
      headerLinks: [
        {
          text: 'Home',
          to: '/'
        },
        {
          text: 'About',
          to: '/about'
        },
        {
          text: 'My Cat',
          to: '/mycat'
        },
        {
          text: 'Resume',
          to: '/resume'
        }
        // {
        //   text: 'Blog',
        //   to: '/blog'
        // }
      ]
    }
  }
}
</script>

<style scoped>
.top-bar {
  @apply bg-secondaryBlueDark p-5 w-full
}
.top-bar-nav {
  @apply flex items-center justify-center gap-2
}
.nav-bar-link {
  @apply font-bold text-primaryLight hover:text-accentColor
}
.nav-bar-link.router-link-active {
  @apply text-accentColor
}
</style>
