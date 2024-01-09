<template>
  <div class="about">
    <h1 class="page-title">A Little About Myself</h1>
    <div class="content-container">
      <div class="text-container">
        <p class="body-intro">Hi my name is Sean Glavin and I decided to make this little website as a practice project for trying out
          frontend web development and a reminder to stay curious and always continue learning!</p>
      </div>
        <div class="text-container">
          <p class="body-interests">In my spare time you may find me doing any of the following:</p>
          <ul class="interests-list">
            <li>Staying active with powerlifting/golf/squash/bouldering</li>
            <li>Perfecting my pourover coffee</li>
            <li>Playing with my cat (check out her pics!)</li>
            <li>Diving down youtube rabbit holes on programming</li>
            <li>Playing computer games with friends</li>
            <li>Checking out a new movie/series</li>
            <li>Winning a game of crib</li>
          </ul>
        </div>
    </div>
  </div>
</template>


<style scoped>
.about {
  @apply flex-col mx-3
}

/* page title css */
.page-title {
  @apply text-2xl text-accentColor underline font-extrabold sm:text-5xl p-5
}

.content-container {
  @apply relative mx-auto max-w-screen-xl px-4 sm:px-6 sm:items-center
}

.text-container {
  @apply max-w-xl text-center ltr:sm:text-left rtl:sm:text-right lg:max-w-2xl p-3 mt-3;
  @apply bg-black rounded-xl bg-opacity-20;
}

.body-intro {
  @apply max-w-sm sm:text-xl/relaxed sm:max-w-lg lg:text-2xl/relaxed lg:max-w-xl text-left
}
.body-interests {
  @apply max-w-sm sm:text-xl/relaxed sm:max-w-lg lg:text-2xl/relaxed lg:max-w-xl text-left text-accentColor2
}
.interests-list {
  @apply list-disc pl-6 mt-4 text-left
}
li {
  @apply mb-2 ml-4
}
li::marker {
  @apply text-accentColor
}
</style>
