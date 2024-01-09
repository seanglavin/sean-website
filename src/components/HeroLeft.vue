<template>
  <!--

    -->

    <div class="hero-container">
      <div class="text-container">
        <h1 class="title">
          Sean Glavin

          <strong class="subtitle"> Welcome to my page. </strong>
        </h1>

        <p class="body">
          Please take a look around and feel free to contact me!
        </p>
        <p class="body">
          This site is a work in progress and will be ever evolving.
        </p>
      </div>
    </div>

</template>

<style scoped>
.hero-container {
  @apply relative mx-auto max-w-screen-xl px-4 py-32 sm:px-6 sm:flex sm:items-center
}
.text-container {
  @apply max-w-xl text-center ltr:sm:text-left rtl:sm:text-right lg:max-w-2xl
}
.title {
  @apply text-3xl font-extrabold sm:text-4xl lg:text-5xl text-left
}
.subtitle {
  @apply block font-extrabold text-accentColor
}
.body {
  @apply mt-4 max-w-sm sm:text-xl/relaxed sm:max-w-lg lg:text-2xl/relaxed lg:max-w-xl text-left
}
</style>
