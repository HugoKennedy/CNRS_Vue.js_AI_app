<script setup>
import { Handle, Position, VueFlow } from '@vue-flow/core'

defineProps({
  tabs: {
    type: Array,
    required: true,
  },
  nodes: {
    type: Array,
    required: true,
  },
  edges: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <section class="main-panel">
    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="{ active: tab === 'Diagramme' }"
      >
        {{ tab }}
      </button>
    </nav>

    <section class="diagram">
      <VueFlow
        class="flow"
        :nodes="nodes"
        :edges="edges"
        fit-view-on-init
      >
        <template #node-scriptNode="{ data }">
          <div class="script-node">
            <Handle
              v-if="data.inputs.length > 0"
              type="target"
              :position="Position.Left"
            />

            <div class="script-node-title">
              {{ data.file }}
            </div>

            <div class="script-node-body">
              <div
                v-for="input in data.inputs"
                :key="`input-${input}`"
              >
                Entree : {{ input }}
              </div>

              <div
                v-for="output in data.outputs"
                :key="`output-${output}`"
              >
                Sortie : {{ output }}
              </div>
            </div>

            <Handle
              v-if="data.outputs.length > 0"
              type="source"
              :position="Position.Right"
            />
          </div>
        </template>
      </VueFlow>
    </section>
  </section>
</template>