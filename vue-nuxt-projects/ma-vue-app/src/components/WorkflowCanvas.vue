<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { Handle, Position, VueFlow } from '@vue-flow/core'
import { useWorkflowStore } from '../stores/workflowStore'

defineProps({
  tabs: {
    type: Array,
    required: true,
  },
})

const workflowStore = useWorkflowStore()
const selectedOutputKey = ref('')

function isNumericArray(values) {
  return (
    Array.isArray(values) &&
    values.length > 0 &&
    values.every((value) => typeof value === 'number')
  )
}

function formatValue(value) {
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value : Number(value.toFixed(4))
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  return value
}

function isEditableElement(element) {
  if (!element) {
    return false
  }

  const tagName = element.tagName?.toLowerCase()

  return (
    tagName === 'input' ||
    tagName === 'textarea' ||
    tagName === 'select' ||
    element.isContentEditable
  )
}

function handleKeyDown(event) {
  const isDeleteKey = event.key === 'Delete' || event.key === 'Backspace'

  if (!isDeleteKey) {
    return
  }

  if (workflowStore.activeTab !== 'Diagramme') {
    return
  }

  if (isEditableElement(document.activeElement)) {
    return
  }

  if (!workflowStore.hasSelection) {
    return
  }

  event.preventDefault()
  workflowStore.deleteSelectedElement()
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

const availableOutputs = computed(() => {
  const outputs = workflowStore.executionResult?.simulatedOutputs || {}

  return Object.entries(outputs)
    .filter(([key]) => key !== 'time' && key !== 'frequencies')
    .map(([key, value]) => ({
      key,
      value,
      type: Array.isArray(value) ? 'liste' : typeof value,
      size: Array.isArray(value) ? value.length : 1,
    }))
})

const currentOutputKey = computed(() => {
  const selectedOutputExists = availableOutputs.value.some(
    (output) => output.key === selectedOutputKey.value,
  )

  if (selectedOutputExists) {
    return selectedOutputKey.value
  }

  return availableOutputs.value[0]?.key || ''
})

const currentOutput = computed(() =>
  availableOutputs.value.find((output) => output.key === currentOutputKey.value),
)

const currentValues = computed(() => {
  const value = currentOutput.value?.value

  if (Array.isArray(value)) {
    return value
  }

  if (value === undefined || value === null) {
    return []
  }

  return [value]
})

const currentXValues = computed(() => {
  const outputs = workflowStore.executionResult?.simulatedOutputs || {}

  if (
    currentOutputKey.value === 'spectre' &&
    Array.isArray(outputs.frequencies) &&
    outputs.frequencies.length === currentValues.value.length
  ) {
    return outputs.frequencies
  }

  if (
    Array.isArray(outputs.time) &&
    outputs.time.length === currentValues.value.length
  ) {
    return outputs.time
  }

  return currentValues.value.map((_, index) => index)
})

const signalPoints = computed(() => {
  if (!isNumericArray(currentValues.value)) {
    return ''
  }

  const width = 600
  const height = 220
  const padding = 24

  const xValues = currentXValues.value
  const yValues = currentValues.value

  const minX = Math.min(...xValues)
  const maxX = Math.max(...xValues)
  const minY = Math.min(...yValues)
  const maxY = Math.max(...yValues)

  return xValues
    .map((xValue, index) => {
      const yValue = yValues[index]

      const x =
        padding +
        ((xValue - minX) / (maxX - minX || 1)) * (width - padding * 2)

      const y =
        height -
        padding -
        ((yValue - minY) / (maxY - minY || 1)) * (height - padding * 2)

      return `${x},${y}`
    })
    .join(' ')
})

const chartPoints = computed(() => {
  if (!isNumericArray(currentValues.value)) {
    return []
  }

  const width = 600
  const height = 220
  const padding = 24

  const xValues = currentXValues.value
  const yValues = currentValues.value

  const minX = Math.min(...xValues)
  const maxX = Math.max(...xValues)
  const minY = Math.min(...yValues)
  const maxY = Math.max(...yValues)

  return yValues.map((yValue, index) => {
    const xValue = xValues[index]

    const x =
      padding +
      ((xValue - minX) / (maxX - minX || 1)) * (width - padding * 2)

    const y =
      height -
      padding -
      ((yValue - minY) / (maxY - minY || 1)) * (height - padding * 2)

    return {
      x,
      y,
    }
  })
})

const tableRows = computed(() =>
  currentValues.value.slice(0, 200).map((value, index) => ({
    index,
    x: currentXValues.value[index],
    value: formatValue(value),
  })),
)

const xColumnLabel = computed(() =>
  currentOutputKey.value === 'spectre' ? 'Frequence' : 'Temps / index',
)

const canDrawChart = computed(() => chartPoints.value.length > 0)

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
      <button
        v-if="workflowStore.hasSelection"
        class="delete-floating-button"
        type="button"
        @click="workflowStore.deleteSelectedElement()"
      >
        Supprimer
      </button>

      <VueFlow
        class="flow"
        v-model:nodes="workflowStore.nodes"
        v-model:edges="workflowStore.edges"
        fit-view-on-init
        @connect="workflowStore.addConnection"
        @node-click="workflowStore.selectNode($event.node.id)"
        @edge-click="workflowStore.selectEdge($event.edge.id)"
        @pane-click="workflowStore.clearSelection"
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

      <p v-else-if="availableOutputs.length === 0">
        Le serveur a repondu, mais aucune sortie affichable n a ete trouvee.
      </p>

      <div v-else>
        <div class="signal-toolbar">
          <label for="signal-output-select">Sortie a afficher</label>

          <select
            id="signal-output-select"
            class="signal-select"
            :value="currentOutputKey"
            @change="selectedOutputKey = $event.target.value"
          >
            <option
              v-for="output in availableOutputs"
              :key="output.key"
              :value="output.key"
            >
              {{ output.key }} - {{ output.type }} - {{ output.size }} valeur(s)
            </option>
          </select>
        </div>

        <div class="signal-card">
          <h3>Sortie serveur : {{ currentOutputKey }}</h3>

          <p class="signal-meta">
            Type : {{ currentOutput?.type }} - Taille : {{ currentOutput?.size }}
          </p>

          <svg
            v-if="canDrawChart"
            class="signal-chart"
            viewBox="0 0 600 220"
            :aria-label="`Courbe de la sortie ${currentOutputKey}`"
            role="img"
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
              v-for="(point, index) in chartPoints"
              :key="index"
              :cx="point.x"
              :cy="point.y"
              r="4"
              class="signal-point"
            />
          </svg>

          <p
            v-else
            class="no-chart-message"
          >
            Cette sortie n est pas une liste numerique. Elle est affichee dans le
            tableau ci-dessous.
          </p>
        </div>

        <table class="signal-table">
          <thead>
            <tr>
              <th>Index</th>
              <th>{{ xColumnLabel }}</th>
              <th>{{ currentOutputKey }}</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="row in tableRows"
              :key="row.index"
            >
              <td>{{ row.index }}</td>
              <td>{{ row.x }}</td>
              <td>{{ row.value }}</td>
            </tr>
          </tbody>
        </table>

        <p
          v-if="currentValues.length > tableRows.length"
          class="table-limit-message"
        >
          Affichage limite aux 200 premieres valeurs sur
          {{ currentValues.length }}.
        </p>
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
          <h4>Parametres modifiables</h4>

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

                <td>
                  <input
                    class="parameter-input"
                    :value="value"
                    @input="
                      workflowStore.updateSelectedNodeParameter(
                        key,
                        $event.target.value
                      )
                    "
                  />
                </td>
              </tr>
            </tbody>
          </table>

          <p v-else>Aucun parametre.</p>
        </div>
      </div>
    </section>
  </section>
</template>

<style scoped>
.delete-floating-button {
  position: absolute;
  z-index: 10;
  top: 12px;
  left: 12px;
  border: none;
  border-radius: 5px;
  padding: 7px 12px;
  background: #dc2626;
  color: white;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.14);
}

.delete-floating-button:hover {
  background: #b91c1c;
}

.signal-toolbar {
  max-width: 700px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.signal-toolbar label {
  font-weight: 700;
}

.signal-select {
  min-width: 280px;
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 5px;
  background: white;
  font: inherit;
}

.signal-meta {
  margin: 0 0 12px;
  color: #4b5563;
  font-size: 14px;
}

.no-chart-message {
  max-width: 700px;
  margin: 0;
  padding: 14px;
  border: 1px solid #fde68a;
  border-radius: 6px;
  background: #fffbeb;
  color: #92400e;
}

.table-limit-message {
  max-width: 700px;
  color: #4b5563;
  font-size: 14px;
}
</style>