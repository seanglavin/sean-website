<template>
  <div class="mtg-game">
    <h1 class="page-title">MTG Art Game</h1>
    <div class="text-container">
      <p class="body-text">
        The first draft of this game is being redesigned. Check back soon!
      </p>
    </div>
  </div>
</template>

<style scoped>
.mtg-game {
  @apply flex-col mx-3
}

.page-title {
  @apply text-2xl text-accentColor underline font-extrabold sm:text-5xl p-5
}

.text-container {
  @apply max-w-xl text-center mx-auto p-3 mt-3;
  @apply bg-black rounded-xl bg-opacity-20;
}

.body-text {
  @apply sm:text-xl/relaxed lg:text-2xl/relaxed
}
</style>
