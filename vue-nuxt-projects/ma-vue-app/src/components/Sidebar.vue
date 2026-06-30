<script setup>
defineProps({
  scriptGroups: {
    type: Array,
    required: true,
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

const emit = defineEmits(['script-click'])
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
          :title="script.description"
          @click="emit('script-click', script)"
        >
          {{ script.file }}
        </button>
      </section>
    </template>
  </aside>
</template>