<script setup>
defineProps({
  title: String,
  actions: Array,
})
</script>

<template>
  <header class="topbar">
    <h1>{{ title }}</h1>

    <div class="actions">
      <button
        v-for="action in actions"
        :key="action"
        :class="{ primary: action === 'Executer' }"
      >
        {{ action }}
      </button>
    </div>
  </header>
</template>