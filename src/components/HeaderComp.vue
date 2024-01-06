<template>
  <header class="top-bar bg-secondaryBlueDark p-7">
    <nav class="top-bar-nav flex items-center justify-center gap-2">
      <!-- Add nav icons later! -->
      <!-- <i class="icon-home"></i> -->
      <router-link class="nav-bar-link font-bold text-primaryLight hover:text-accentColor"
        v-for="(link, index) in headerLinks" :key="index" :to="link.to">
        <span>{{ link.text }}</span>
        <!-- add a | between each link -->
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
.nav-bar-link.router-link-active {
  @apply text-accentColor
}
</style>
