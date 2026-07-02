<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { Handle, Position, VueFlow, useVueFlow } from '@vue-flow/core'
import { useWorkflowStore } from '../stores/workflowStore'

defineProps({
  tabs: {
    type: Array,
    required: true,
  },
})

const workflowStore = useWorkflowStore()
const selectedOutputKey = ref('')
const selectedComparisonKeys = ref([])

const seriesColors = ['#2563eb', '#dc2626', '#059669', '#7c3aed', '#ea580c']

const { screenToFlowCoordinate } = useVueFlow()

function handleDragOver(event) {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'copy'
}

function handleScriptDrop(event) {
  event.preventDefault()

  const scriptId = event.dataTransfer?.getData('application/x-script-id')

  if (!scriptId) {
    return
  }

  const position = screenToFlowCoordinate({
    x: event.clientX,
    y: event.clientY,
  })

  workflowStore.addScriptNodeFromLibrary(scriptId, position)
}

function isNumericArray(values) {
  return (
    Array.isArray(values) &&
    values.length > 0 &&
    values.every((value) => typeof value === 'number')
  )
}

function isInternalOutputKey(key) {
  return key === 'time' || key === 'frequencies' || key.startsWith('__thinkml_')
}

function formatNumber(value) {
  if (typeof value !== 'number') {
    return value
  }

  if (value === 0) {
    return '0'
  }

  const absoluteValue = Math.abs(value)

  if (absoluteValue >= 10000 || absoluteValue < 0.001) {
    return value.toExponential(2)
  }

  return Number(value.toFixed(4)).toString()
}

function formatValue(value) {
  if (typeof value === 'number') {
    return formatNumber(value)
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  return value
}

function formatUnit(unit) {
  return unit ? ` ${unit}` : ''
}

function getOutputOptionLabel(output) {
  const metadata = output.metadata || {}
  const unit = metadata.unit || ''
  const xLabel = metadata.xLabel || 'Temps / index'
  const xUnit = metadata.xUnit || ''

  if (output.kind === 'courbe') {
    const xPart = xUnit ? `${xLabel} (${xUnit})` : xLabel
    const yPart = unit || 'sans unite'

    return `${output.label} | ${output.size} points | ${yPart} en fonction de ${xPart}`
  }

  if (output.kind === 'valeur') {
    const value = Array.isArray(output.value) ? output.value[0] : output.value
    return `${output.label} = ${formatValue(value)}${formatUnit(unit)}`
  }

  return `${output.label} | ${output.size} valeur(s)`
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

function toggleComparisonKey(key, checked) {
  if (checked) {
    selectedComparisonKeys.value = [...new Set([...selectedComparisonKeys.value, key])]
    return
  }

  selectedComparisonKeys.value = selectedComparisonKeys.value.filter(
    (currentKey) => currentKey !== key,
  )
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

const rawOutputs = computed(() => workflowStore.executionResult?.simulatedOutputs || {})
const outputMetadata = computed(() => rawOutputs.value.__thinkml_outputs || {})

const availableOutputs = computed(() => {
  return Object.entries(rawOutputs.value)
    .filter(([key]) => !isInternalOutputKey(key))
    .map(([key, value]) => {
      const metadata = outputMetadata.value[key] || {}
      const isList = Array.isArray(value)
      const isNumericList = isNumericArray(value)

      let kind = typeof value

      if (isList && value.length > 1 && isNumericList) {
        kind = 'courbe'
      } else if (isList && value.length <= 1) {
        kind = 'valeur'
      } else if (isList) {
        kind = 'liste'
      } else if (typeof value === 'number') {
        kind = 'valeur'
      }

      const output = {
        key,
        value,
        metadata,
        label: metadata.label || key,
        unit: metadata.unit || '',
        kind,
        size: isList ? value.length : 1,
      }

      return {
        ...output,
        optionLabel: getOutputOptionLabel(output),
      }
    })
})

const curveOutputs = computed(() =>
  availableOutputs.value.filter((output) => output.kind === 'courbe'),
)

const scalarOutputs = computed(() =>
  availableOutputs.value.filter((output) => output.kind === 'valeur'),
)

const listOutputs = computed(() =>
  availableOutputs.value.filter(
    (output) => output.kind !== 'courbe' && output.kind !== 'valeur',
  ),
)

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

const currentMetadata = computed(
  () => outputMetadata.value[currentOutputKey.value] || {},
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

function getXValuesForOutput(output) {
  const metadata = output.metadata || {}
  const value = Array.isArray(output.value) ? output.value : [output.value]
  const xKey = metadata.xKey

  if (
    xKey &&
    Array.isArray(rawOutputs.value[xKey]) &&
    rawOutputs.value[xKey].length === value.length
  ) {
    return rawOutputs.value[xKey]
  }

  if (
    output.key === 'spectre' &&
    Array.isArray(rawOutputs.value.frequencies) &&
    rawOutputs.value.frequencies.length === value.length
  ) {
    return rawOutputs.value.frequencies
  }

  if (
    Array.isArray(rawOutputs.value.time) &&
    rawOutputs.value.time.length === value.length
  ) {
    return rawOutputs.value.time
  }

  return value.map((_, index) => index)
}

const currentXValues = computed(() => {
  if (!currentOutput.value) {
    return []
  }

  return getXValuesForOutput(currentOutput.value)
})

const comparisonCandidates = computed(() => {
  if (!currentOutput.value || currentOutput.value.kind !== 'courbe') {
    return []
  }

  return curveOutputs.value.filter((output) => {
    if (output.key === currentOutputKey.value) {
      return false
    }

    return output.value.length === currentValues.value.length
  })
})

const selectedComparisonOutputs = computed(() =>
  comparisonCandidates.value.filter((output) =>
    selectedComparisonKeys.value.includes(output.key),
  ),
)

const canDrawChart = computed(
  () => isNumericArray(currentValues.value) && currentValues.value.length > 1,
)

const chartSeries = computed(() => {
  if (!canDrawChart.value || !currentOutput.value) {
    return []
  }

  const outputs = [currentOutput.value, ...selectedComparisonOutputs.value]

  return outputs.map((output, index) => ({
    key: output.key,
    label: output.label,
    unit: output.unit,
    color: seriesColors[index % seriesColors.length],
    xValues: getXValuesForOutput(output),
    yValues: output.value,
  }))
})

const chartConfig = {
  width: 720,
  height: 320,
  left: 72,
  right: 24,
  top: 28,
  bottom: 64,
}

const chartBounds = computed(() => {
  const allXValues = chartSeries.value.flatMap((series) => series.xValues)
  const allYValues = chartSeries.value.flatMap((series) => series.yValues)

  const minX = Math.min(...allXValues)
  const maxX = Math.max(...allXValues)
  const minY = Math.min(...allYValues)
  const maxY = Math.max(...allYValues)

  const yPadding = (maxY - minY || 1) * 0.08

  return {
    minX,
    maxX,
    minY: minY - yPadding,
    maxY: maxY + yPadding,
  }
})

function getChartX(xValue) {
  const bounds = chartBounds.value
  const drawingWidth = chartConfig.width - chartConfig.left - chartConfig.right

  return (
    chartConfig.left +
    ((xValue - bounds.minX) / (bounds.maxX - bounds.minX || 1)) * drawingWidth
  )
}

function getChartY(yValue) {
  const bounds = chartBounds.value
  const drawingHeight = chartConfig.height - chartConfig.top - chartConfig.bottom

  return (
    chartConfig.height -
    chartConfig.bottom -
    ((yValue - bounds.minY) / (bounds.maxY - bounds.minY || 1)) * drawingHeight
  )
}

const renderedSeries = computed(() =>
  chartSeries.value.map((series) => ({
    ...series,
    points: series.yValues
      .map((yValue, index) => `${getChartX(series.xValues[index])},${getChartY(yValue)}`)
      .join(' '),
    circles: series.yValues.map((yValue, index) => ({
      x: getChartX(series.xValues[index]),
      y: getChartY(yValue),
    })),
  })),
)

function buildTicks(minValue, maxValue, count = 5) {
  if (count <= 1) {
    return [minValue]
  }

  const ticks = []

  for (let index = 0; index < count; index++) {
    const ratio = index / (count - 1)
    ticks.push(minValue + (maxValue - minValue) * ratio)
  }

  return ticks
}

const xTicks = computed(() => {
  if (!canDrawChart.value) {
    return []
  }

  const bounds = chartBounds.value

  return buildTicks(bounds.minX, bounds.maxX).map((value) => ({
    value,
    x: getChartX(value),
    label: formatNumber(value),
  }))
})

const yTicks = computed(() => {
  if (!canDrawChart.value) {
    return []
  }

  const bounds = chartBounds.value

  return buildTicks(bounds.minY, bounds.maxY).map((value) => ({
    value,
    y: getChartY(value),
    label: formatNumber(value),
  }))
})

const xAxisLabel = computed(() => currentMetadata.value.xLabel || 'Temps / index')
const xAxisUnit = computed(() => currentMetadata.value.xUnit || '')
const yAxisLabel = computed(() => currentMetadata.value.label || currentOutputKey.value)
const yAxisUnit = computed(() => currentMetadata.value.unit || '')

const fullXAxisLabel = computed(() => {
  if (!xAxisUnit.value) {
    return xAxisLabel.value
  }

  return `${xAxisLabel.value} (${xAxisUnit.value})`
})

const fullYAxisLabel = computed(() => {
  if (!yAxisUnit.value) {
    return yAxisLabel.value
  }

  return `${yAxisLabel.value} (${yAxisUnit.value})`
})

const isScalarOutput = computed(() => {
  if (!currentOutput.value) {
    return false
  }

  return !Array.isArray(currentOutput.value.value) || currentValues.value.length <= 1
})

const scalarDisplayValue = computed(() => {
  if (!currentValues.value.length) {
    return 'Aucune valeur'
  }

  return formatValue(currentValues.value[0])
})

const tableRows = computed(() =>
  currentValues.value.slice(0, 200).map((value, index) => ({
    index,
    x: currentXValues.value[index],
    value: formatValue(value),
  })),
)

const selectedNodeParameterRows = computed(() => {
  const node = workflowStore.selectedNode

  if (!node) {
    return []
  }

  const parameters = node.data.parameters || {}
  const parameterMetadata = node.data.parameterMetadata || {}

  return Object.entries(parameters).map(([key, value]) => {
    const metadata = parameterMetadata[key] || {}

    return {
      key,
      value,
      label: metadata.label || key,
      unit: metadata.unit || '',
      description: metadata.description || '',
      type: metadata.type || (typeof value === 'number' ? 'number' : 'text'),
      min: metadata.min,
      max: metadata.max,
      step: metadata.step || (typeof value === 'number' ? 'any' : undefined),
    }
  })
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
        @dragover="handleDragOver"
        @drop="handleScriptDrop"
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
          <label for="signal-output-select">Sortie principale</label>

          <select
            id="signal-output-select"
            class="signal-select"
            :value="currentOutputKey"
            @change="selectedOutputKey = $event.target.value"
          >
            <optgroup
              v-if="curveOutputs.length > 0"
              label="Courbes"
            >
              <option
                v-for="output in curveOutputs"
                :key="output.key"
                :value="output.key"
              >
                {{ output.optionLabel }}
              </option>
            </optgroup>

            <optgroup
              v-if="scalarOutputs.length > 0"
              label="Valeurs"
            >
              <option
                v-for="output in scalarOutputs"
                :key="output.key"
                :value="output.key"
              >
                {{ output.optionLabel }}
              </option>
            </optgroup>

            <optgroup
              v-if="listOutputs.length > 0"
              label="Autres sorties"
            >
              <option
                v-for="output in listOutputs"
                :key="output.key"
                :value="output.key"
              >
                {{ output.optionLabel }}
              </option>
            </optgroup>
          </select>
        </div>

        <div
          v-if="comparisonCandidates.length > 0"
          class="comparison-panel"
        >
          <strong>Comparer avec :</strong>

          <label
            v-for="output in comparisonCandidates"
            :key="output.key"
            class="comparison-option"
          >
            <input
              type="checkbox"
              :checked="selectedComparisonKeys.includes(output.key)"
              @change="toggleComparisonKey(output.key, $event.target.checked)"
            />
            {{ output.label }}
          </label>
        </div>

        <div class="signal-card">
          <div class="signal-card-header">
            <div>
              <h3>{{ yAxisLabel }}</h3>

              <p class="signal-meta">
                Cle JSON : {{ currentOutputKey }}
                <span v-if="yAxisUnit"> - Unite : {{ yAxisUnit }}</span>
              </p>
            </div>
          </div>

          <div
            v-if="isScalarOutput"
            class="scalar-value-card"
          >
            <span class="scalar-label">{{ yAxisLabel }}</span>

            <strong class="scalar-value">
              {{ scalarDisplayValue }}
              <span v-if="yAxisUnit">{{ yAxisUnit }}</span>
            </strong>
          </div>

          <svg
            v-else-if="canDrawChart"
            class="signal-chart"
            viewBox="0 0 720 320"
            :aria-label="`Courbe de la sortie ${currentOutputKey}`"
            role="img"
          >
            <line
              :x1="chartConfig.left"
              :y1="chartConfig.height - chartConfig.bottom"
              :x2="chartConfig.width - chartConfig.right"
              :y2="chartConfig.height - chartConfig.bottom"
              class="axis"
            />

            <line
              :x1="chartConfig.left"
              :y1="chartConfig.top"
              :x2="chartConfig.left"
              :y2="chartConfig.height - chartConfig.bottom"
              class="axis"
            />

            <g
              v-for="tick in xTicks"
              :key="`x-${tick.label}`"
            >
              <line
                :x1="tick.x"
                :y1="chartConfig.top"
                :x2="tick.x"
                :y2="chartConfig.height - chartConfig.bottom"
                class="grid-line"
              />

              <text
                :x="tick.x"
                :y="chartConfig.height - chartConfig.bottom + 24"
                class="axis-tick"
                text-anchor="middle"
              >
                {{ tick.label }}
              </text>
            </g>

            <g
              v-for="tick in yTicks"
              :key="`y-${tick.label}`"
            >
              <line
                :x1="chartConfig.left"
                :y1="tick.y"
                :x2="chartConfig.width - chartConfig.right"
                :y2="tick.y"
                class="grid-line"
              />

              <text
                :x="chartConfig.left - 10"
                :y="tick.y + 4"
                class="axis-tick"
                text-anchor="end"
              >
                {{ tick.label }}
              </text>
            </g>

            <g
              v-for="series in renderedSeries"
              :key="series.key"
            >
              <polyline
                :points="series.points"
                class="signal-line"
                :style="{ stroke: series.color }"
              />

              <circle
                v-for="(point, index) in series.circles"
                :key="`${series.key}-${index}`"
                :cx="point.x"
                :cy="point.y"
                r="2.6"
                class="signal-point"
                :style="{ fill: series.color }"
              />
            </g>

            <text
              :x="chartConfig.width / 2"
              :y="chartConfig.height - 16"
              class="axis-label"
              text-anchor="middle"
            >
              {{ fullXAxisLabel }}
            </text>

            <text
              :x="-chartConfig.height / 2"
              y="18"
              class="axis-label"
              text-anchor="middle"
              transform="rotate(-90)"
            >
              {{ fullYAxisLabel }}
            </text>
          </svg>

          <div
            v-if="renderedSeries.length > 1"
            class="chart-legend"
          >
            <span
              v-for="series in renderedSeries"
              :key="series.key"
              class="legend-item"
            >
              <span
                class="legend-color"
                :style="{ background: series.color }"
              />
              {{ series.label }}
            </span>
          </div>

          <p
            v-if="!isScalarOutput && !canDrawChart"
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
              <th>{{ fullXAxisLabel }}</th>
              <th>{{ fullYAxisLabel }}</th>
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

          <div
            v-if="selectedNodeParameterRows.length > 0"
            class="parameter-list"
          >
            <label
              v-for="parameter in selectedNodeParameterRows"
              :key="parameter.key"
              class="parameter-field"
            >
              <span class="parameter-label">
                {{ parameter.label }}
                <small v-if="parameter.unit">({{ parameter.unit }})</small>
              </span>

              <input
                class="parameter-input"
                :type="parameter.type === 'number' ? 'number' : 'text'"
                :value="parameter.value"
                :min="parameter.min"
                :max="parameter.max"
                :step="parameter.step"
                @input="
                  workflowStore.updateSelectedNodeParameter(
                    parameter.key,
                    $event.target.value
                  )
                "
              />

              <span
                v-if="parameter.description"
                class="parameter-description"
              >
                {{ parameter.description }}
              </span>
            </label>
          </div>

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
  max-width: 900px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.signal-toolbar label {
  font-weight: 700;
}

.signal-select {
  min-width: 560px;
  max-width: 100%;
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 5px;
  background: white;
}

.comparison-panel {
  max-width: 900px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px 14px;
  margin-bottom: 16px;
  padding: 10px 12px;
  border: 1px solid #dbeafe;
  border-radius: 8px;
  background: #eff6ff;
}

.comparison-option {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.signal-card {
  max-width: 900px;
}

.signal-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.signal-card h3 {
  margin: 0 0 6px;
  font-size: 18px;
}

.signal-meta {
  margin: 0;
  color: #475569;
  font-size: 14px;
}

.scalar-value-card {
  display: inline-flex;
  flex-direction: column;
  gap: 8px;
  min-width: 260px;
  padding: 18px 20px;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  background: white;
}

.scalar-label {
  color: #475569;
  font-size: 14px;
}

.scalar-value {
  color: #1d4ed8;
  font-size: 28px;
}

.signal-chart {
  width: 100%;
  max-width: 760px;
  height: auto;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
}

.axis {
  stroke: #64748b;
  stroke-width: 2;
}

.grid-line {
  stroke: #e5e7eb;
  stroke-width: 1;
}

.axis-tick {
  fill: #475569;
  font-size: 12px;
}

.axis-label {
  fill: #111827;
  font-size: 13px;
  font-weight: 700;
}

.signal-line {
  fill: none;
  stroke-width: 3;
}

.signal-point {
  opacity: 0.9;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-top: 10px;
  font-size: 14px;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 999px;
}

.no-chart-message {
  margin: 0;
  padding: 12px;
  border: 1px solid #fed7aa;
  border-radius: 8px;
  background: #fff7ed;
  color: #9a3412;
}

.signal-table {
  max-width: 900px;
  width: 100%;
  margin-top: 24px;
  border-collapse: collapse;
  background: white;
}

.signal-table th,
.signal-table td {
  border: 1px solid #d1d5db;
  padding: 9px 12px;
  text-align: left;
}

.signal-table th {
  background: #f3f4f6;
}

.table-limit-message {
  color: #475569;
  font-size: 14px;
}

.parameters-card {
  max-width: 900px;
  padding: 18px;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  background: #eff6ff;
}

.parameters-card h3 {
  margin-top: 0;
}

.parameters-section {
  margin-top: 18px;
}

.parameter-list {
  display: grid;
  gap: 14px;
}

.parameter-field {
  display: grid;
  grid-template-columns: minmax(180px, 260px) minmax(180px, 1fr);
  gap: 8px 14px;
  align-items: center;
  padding: 12px;
  border: 1px solid #dbeafe;
  border-radius: 8px;
  background: white;
}

.parameter-label {
  font-weight: 700;
}

.parameter-label small {
  color: #475569;
  font-weight: 400;
}

.parameter-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 5px;
  font: inherit;
}

.parameter-description {
  grid-column: 1 / -1;
  color: #475569;
  font-size: 13px;
}
</style>