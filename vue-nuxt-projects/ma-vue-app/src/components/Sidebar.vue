<script setup>
defineProps({
  scriptGroups: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <aside class="sidebar">
    <h2>Espaces de travail</h2>

    <section
      v-for="group in scriptGroups"
      :key="group.title"
      class="script-group"
    >
      <h3>{{ group.title }}</h3>

      <button
        v-for="script in group.scripts"
        :key="script"
        class="script"
      >
        {{ script }}
      </button>
    </section>
  </aside>
</template>