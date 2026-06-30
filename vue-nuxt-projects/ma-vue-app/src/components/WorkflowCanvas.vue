<script setup>
import { computed } from 'vue'
import { Handle, Position, VueFlow } from '@vue-flow/core'
import { useWorkflowStore } from '../stores/workflowStore'

defineProps({
  tabs: {
    type: Array,
    required: true,
  },
})

const workflowStore = useWorkflowStore()

const signalPoints = computed(() => {
  const outputs = workflowStore.executionResult?.simulatedOutputs

  if (!outputs || !outputs.time || !outputs.signal) {
    return ''
  }

  const width = 600
  const height = 220
  const padding = 24

  const times = outputs.time
  const values = outputs.signal

  const minX = Math.min(...times)
  const maxX = Math.max(...times)
  const minY = Math.min(...values)
  const maxY = Math.max(...values)

  return times
    .map((time, index) => {
      const value = values[index]

      const x =
        padding +
        ((time - minX) / (maxX - minX || 1)) * (width - padding * 2)

      const y =
        height -
        padding -
        ((value - minY) / (maxY - minY || 1)) * (height - padding * 2)

      return `${x},${y}`
    })
    .join(' ')
})

const selectedNodeParameters = computed(() => {
  const parameters = workflowStore.selectedNode?.data.parameters || {}

  return Object.entries(parameters)
})
</script>

<template>
  <section class="main-panel">
    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="{ active: tab === workflowStore.activeTab }"
        @click="workflowStore.setActiveTab(tab)"
      >
        {{ tab }}
      </button>
    </nav>

    <section
      v-if="workflowStore.activeTab === 'Diagramme'"
      class="diagram"
    >
      <VueFlow
        class="flow"
        v-model:nodes="workflowStore.nodes"
        v-model:edges="workflowStore.edges"
        fit-view-on-init
        @connect="workflowStore.addConnection"
        @node-click="workflowStore.selectNode($event.node.id)"
      >
        <template #node-scriptNode="{ id, data }">
          <div
            class="script-node"
            :class="{ selected: id === workflowStore.selectedNodeId }"
          >
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

    <section
      v-else-if="workflowStore.activeTab === 'Signaux'"
      class="panel-content"
    >
      <h2>Signaux simules</h2>

      <p v-if="!workflowStore.executionResult">
        Aucun signal disponible. Lance d abord une execution.
      </p>

      <div v-else>
        <div class="signal-card">
          <h3>Signal temporel retourne par le serveur</h3>

          <svg
            class="signal-chart"
            viewBox="0 0 600 220"
            role="img"
            aria-label="Courbe du signal simule"
          >
            <line
              x1="24"
              y1="196"
              x2="576"
              y2="196"
              class="axis"
            />
            <line
              x1="24"
              y1="24"
              x2="24"
              y2="196"
              class="axis"
            />

            <polyline
              :points="signalPoints"
              class="signal-line"
            />

            <circle
              v-for="(value, index) in workflowStore.executionResult.simulatedOutputs.signal"
              :key="index"
              :cx="
                24 +
                (index /
                  (workflowStore.executionResult.simulatedOutputs.signal.length - 1 || 1)) *
                  552
              "
              :cy="196 - value * 172"
              r="4"
              class="signal-point"
            />
          </svg>
        </div>

        <table class="signal-table">
          <thead>
            <tr>
              <th>Index</th>
              <th>Temps</th>
              <th>Signal</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="(time, index) in workflowStore.executionResult.simulatedOutputs.time"
              :key="index"
            >
              <td>{{ index }}</td>
              <td>{{ time }}</td>
              <td>{{ workflowStore.executionResult.simulatedOutputs.signal[index] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section
      v-else-if="workflowStore.activeTab === 'Logs'"
      class="panel-content"
    >
      <h2>Logs d execution</h2>

      <p
        v-if="workflowStore.isRunning"
        class="status-message"
      >
        Execution en cours...
      </p>

      <p
        v-if="workflowStore.executionError"
        class="error-message"
      >
        {{ workflowStore.executionError }}
      </p>

      <ul class="logs-list">
        <li
          v-for="log in workflowStore.executionLogs"
          :key="log"
        >
          {{ log }}
        </li>
      </ul>

      <div
        v-if="workflowStore.executionResult"
        class="result-box"
      >
        <h3>Resultat serveur</h3>

        <p>Status : {{ workflowStore.executionResult.status }}</p>
        <p>Message : {{ workflowStore.executionResult.message }}</p>
        <p>Blocs : {{ workflowStore.executionResult.nodeCount }}</p>
        <p>Connexions : {{ workflowStore.executionResult.edgeCount }}</p>
        <p>
          Ordre :
          {{ workflowStore.executionResult.executionOrder.join(' -> ') }}
        </p>
      </div>
    </section>

    <section
      v-else-if="workflowStore.activeTab === 'Parametres'"
      class="panel-content"
    >
      <h2>Parametres du bloc</h2>

      <p v-if="!workflowStore.selectedNode">
        Aucun bloc selectionne. Clique sur un bloc dans le diagramme.
      </p>

      <div
        v-else
        class="parameters-card"
      >
        <h3>{{ workflowStore.selectedNode.data.file }}</h3>

        <p>
          <strong>Label :</strong>
          {{ workflowStore.selectedNode.data.label || 'Non defini' }}
        </p>

        <p>
          <strong>Description :</strong>
          {{ workflowStore.selectedNode.data.description || 'Aucune description' }}
        </p>

        <div class="parameters-section">
          <h4>Entrees</h4>
          <ul>
            <li
              v-for="input in workflowStore.selectedNode.data.inputs"
              :key="input"
            >
              {{ input }}
            </li>
            <li v-if="workflowStore.selectedNode.data.inputs.length === 0">
              Aucune entree
            </li>
          </ul>
        </div>

        <div class="parameters-section">
          <h4>Sorties</h4>
          <ul>
            <li
              v-for="output in workflowStore.selectedNode.data.outputs"
              :key="output"
            >
              {{ output }}
            </li>
            <li v-if="workflowStore.selectedNode.data.outputs.length === 0">
              Aucune sortie
            </li>
          </ul>
        </div>

        <div class="parameters-section">
          <h4>Parametres</h4>

          <table
            v-if="selectedNodeParameters.length > 0"
            class="parameters-table"
          >
            <thead>
              <tr>
                <th>Nom</th>
                <th>Valeur</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="[key, value] in selectedNodeParameters"
                :key="key"
              >
                <td>{{ key }}</td>
                <td>{{ value }}</td>
              </tr>
            </tbody>
          </table>

          <p v-else>Aucun parametre.</p>
        </div>
      </div>
    </section>
  </section>
</template>