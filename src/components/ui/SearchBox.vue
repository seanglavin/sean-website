<template>
  <div class="search-box">
    <label class="sr-only" :for="inputId">{{ label }}</label>
    <input
      :id="inputId"
      class="search-input"
      type="search"
      :value="modelValue"
      :placeholder="placeholder"
      @input="onInput"
      @keydown.escape="clear"
    />
    <button v-if="modelValue" class="clear-button" type="button" @click="clear">
      Clear
    </button>
  </div>
</template>

<script setup>
import { onUnmounted } from 'vue'

let idSeq = 0

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: 'Search' },
  placeholder: { type: String, default: 'Search…' },
  debounce: { type: Number, default: 150 },
})
const emit = defineEmits(['update:modelValue'])

const inputId = `search-box-${++idSeq}`
let timer = null

function onInput(event) {
  const value = event.target.value
  clearTimeout(timer)
  timer = setTimeout(() => emit('update:modelValue', value), props.debounce)
}

function clear() {
  clearTimeout(timer)
  emit('update:modelValue', '')
}

onUnmounted(() => clearTimeout(timer))
</script>

<style scoped>
.search-box {
  @apply flex items-center gap-2 w-full
}
.search-input {
  @apply flex-1 px-3 py-2 rounded-lg bg-black bg-opacity-30 text-textColor;
  @apply border border-transparent focus:border-accentColor focus:outline-none;
}
.clear-button {
  @apply px-3 py-2 rounded-lg font-bold bg-black bg-opacity-20 hover:text-accentColor
}
</style>
