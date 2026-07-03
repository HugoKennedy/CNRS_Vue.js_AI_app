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

const emit = defineEmits(['script-select', 'script-drag-start', 'group-delete'])
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
        <div class="script-group-header">
          <h3>{{ group.title }}</h3>

          <button
            type="button"
            class="delete-group-button"
            :title="`Supprimer la categorie ${group.title}`"
            @click="emit('group-delete', group.title)"
          >
            x
          </button>
        </div>

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
.script-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.script-group-header h3 {
  margin: 0;
}

.delete-group-button {
  width: 22px;
  height: 22px;
  flex: 0 0 auto;
  border: 1px solid #fecaca;
  border-radius: 999px;
  background: #fee2e2;
  color: #b91c1c;
  font-size: 13px;
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
}

.delete-group-button:hover {
  border-color: #ef4444;
  background: #fecaca;
  color: #7f1d1d;
}

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