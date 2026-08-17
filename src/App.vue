<template>
  <a href="#main-content" class="skip-link">Skip to content</a>
  <HeaderComp />
  <main id="main-content" class="router-view-container">
    <router-view />
  </main>
  <FooterComp />
</template>

<script setup>
import FooterComp from '@/components/FooterComp.vue'
import HeaderComp from '@/components/HeaderComp.vue'
</script>

<style>
#app {
  min-height: 100vh;
  min-width: 375px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: var(--color-text);
  background-color: var(--color-bg);
  background-image: url('@/assets/images/sideprofileoverlay2-removebg.png');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: top right;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  /* align-items: center; */
}

.router-view-container {
  @apply flex-1
}

.skip-link {
  @apply sr-only focus:not-sr-only fixed top-2 left-2 z-50 bg-accentColor text-onAccent px-4 py-2 rounded font-bold;
}
</style>
