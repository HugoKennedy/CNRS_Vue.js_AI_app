<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  actions: {
    type: Array,
    required: true,
  },
})

const emit = defineEmits(['action-click'])
</script>

<template>
  <header class="topbar">
    <h1>{{ title }}</h1>

    <div class="actions">
      <button
        v-for="action in actions"
        :key="action"
        :class="{ primary: action === 'Executer' }"
        @click="emit('action-click', action)"
      >
        {{ action }}
      </button>
    </div>
  </header>
</template>