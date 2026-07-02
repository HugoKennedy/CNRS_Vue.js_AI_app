<script setup>
defineProps({
  scriptGroups: {
    type: Array,
    required: true,
  },
  selectedScriptId: {
    type: String,
    default: '',
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  errorMessage: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['script-select', 'script-drag-start'])
</script>

<template>
  <aside class="sidebar">
    <h2>Espaces de travail</h2>

    <p
      v-if="isLoading"
      class="sidebar-status"
    >
      Chargement des scripts...
    </p>

    <p
      v-else-if="errorMessage"
      class="sidebar-error"
    >
      Erreur : {{ errorMessage }}
    </p>

    <template v-else>
      <section
        v-for="group in scriptGroups"
        :key="group.title"
        class="script-group"
      >
        <h3>{{ group.title }}</h3>

        <button
          v-for="script in group.scripts"
          :key="script.id"
          class="script"
          :class="{ selected: script.id === selectedScriptId }"
          :title="`${script.description} | Glisser vers le diagramme pour creer un bloc`"
          draggable="true"
          @click="emit('script-select', script)"
          @dragstart="emit('script-drag-start', { event: $event, script })"
        >
          {{ script.file }}
        </button>
      </section>
    </template>
  </aside>
</template>

<style scoped>
.script {
  cursor: grab;
}

.script:active {
  cursor: grabbing;
}

.script.selected {
  background: #fee2e2;
  border-color: #ef4444;
  border-left-color: #dc2626;
  color: #7f1d1d;
  font-weight: 700;
}
</style>