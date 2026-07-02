<script setup>
import { computed, onMounted, ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import TopBar from './components/TopBar.vue'
import WorkflowCanvas from './components/WorkflowCanvas.vue'
import { useWorkflowStore } from './stores/workflowStore'

const workflowStore = useWorkflowStore()

const isImportModalOpen = ref(false)
const selectedFile = ref(null)
const selectedGroup = ref('Detection APD')
const isImporting = ref(false)

workflowStore.loadWorkflow()

onMounted(() => {
  workflowStore.loadScripts()
})

const selectedFileName = computed(() => selectedFile.value?.name || '')

function openImportModal() {
  selectedFile.value = null
  selectedGroup.value = 'Detection APD'
  workflowStore.importScriptStatus = ''
  workflowStore.importScriptError = ''
  isImportModalOpen.value = true
}

function closeImportModal() {
  if (isImporting.value) {
    return
  }

  isImportModalOpen.value = false
}

function handleFileChange(event) {
  selectedFile.value = event.target.files?.[0] || null
  workflowStore.importScriptStatus = ''
  workflowStore.importScriptError = ''
}

async function submitScriptImport() {
  isImporting.value = true

  const success = await workflowStore.importPythonScript({
    file: selectedFile.value,
    group: selectedGroup.value,
  })

  isImporting.value = false

  if (success) {
    selectedFile.value = null
    isImportModalOpen.value = false
  }
}

function handleActionClick(action) {
  if (action === 'Sauvegarder') {
    workflowStore.saveWorkflow()
  }

  if (action === 'Reinitialiser' || action === 'Nouveau espace') {
    workflowStore.resetWorkflow()
  }

  if (action === 'Ajouter script') {
    openImportModal()
  }

  if (action === 'Executer') {
    workflowStore.runWorkflow()
  }
}

function handleScriptSelect(script) {
  workflowStore.selectScript(script.id)
}

function handleScriptDragStart({ event, script }) {
  workflowStore.selectScript(script.id)

  event.dataTransfer.effectAllowed = 'copy'
  event.dataTransfer.setData('application/x-script-id', script.id)
  event.dataTransfer.setData('text/plain', script.file)
}
</script>

<template>
  <div class="app-shell">
    <TopBar
      title="ThinkML"
      :actions="workflowStore.actions"
      @action-click="handleActionClick"
    />

    <main class="workspace">
      <Sidebar
        :script-groups="workflowStore.scriptGroups"
        :selected-script-id="workflowStore.selectedScriptId"
        :is-loading="workflowStore.isLoadingScripts"
        :error-message="workflowStore.scriptsError"
        @script-select="handleScriptSelect"
        @script-drag-start="handleScriptDragStart"
      />

      <WorkflowCanvas :tabs="workflowStore.tabs" />
    </main>

    <div
      v-if="isImportModalOpen"
      class="modal-backdrop"
      @click.self="closeImportModal"
    >
      <section class="import-modal">
        <header class="import-modal-header">
          <h2>Ajouter un script Python</h2>

          <button
            type="button"
            class="modal-close-button"
            @click="closeImportModal"
          >
            x
          </button>
        </header>

        <div class="import-form">
          <label class="form-label">
            Fichier Python
            <input
              type="file"
              accept=".py"
              class="file-input"
              @change="handleFileChange"
            />
          </label>

          <p
            v-if="selectedFileName"
            class="selected-file"
          >
            Fichier selectionne : {{ selectedFileName }}
          </p>

          <label class="form-label">
            Categorie
            <select
              v-model="selectedGroup"
              class="category-select"
            >
              <option value="Detection APD">Detection APD</option>
              <option value="FPGA JESD204B">FPGA JESD204B</option>
            </select>
          </label>

          <p class="modal-help">
            Le script doit lire un JSON depuis stdin et renvoyer un JSON avec
            print(json.dumps(...)).
          </p>

          <p
            v-if="workflowStore.importScriptError"
            class="import-error"
          >
            {{ workflowStore.importScriptError }}
          </p>

          <p
            v-if="workflowStore.importScriptStatus"
            class="import-success"
          >
            {{ workflowStore.importScriptStatus }}
          </p>
        </div>

        <footer class="import-modal-actions">
          <button
            type="button"
            class="secondary-button"
            @click="closeImportModal"
          >
            Annuler
          </button>

          <button
            type="button"
            class="primary-button"
            :disabled="isImporting"
            @click="submitScriptImport"
          >
            {{ isImporting ? 'Verification...' : 'Ajouter' }}
          </button>
        </footer>
      </section>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.38);
}

.import-modal {
  width: 440px;
  max-width: calc(100vw - 32px);
  border-radius: 8px;
  background: white;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.24);
}

.import-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.import-modal-header h2 {
  margin: 0;
  font-size: 18px;
}

.modal-close-button {
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
}

.import-form {
  padding: 20px;
}

.form-label {
  display: block;
  margin-bottom: 16px;
  font-weight: 700;
}

.file-input,
.category-select {
  width: 100%;
  margin-top: 8px;
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 5px;
  font: inherit;
}

.selected-file {
  margin: -6px 0 16px;
  color: #374151;
  font-size: 14px;
}

.modal-help {
  margin: 0;
  padding: 12px;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  background: #eff6ff;
  color: #1f2937;
  font-size: 14px;
}

.import-error {
  margin: 14px 0 0;
  color: #b91c1c;
  font-size: 14px;
  font-weight: 700;
}

.import-success {
  margin: 14px 0 0;
  color: #047857;
  font-size: 14px;
  font-weight: 700;
}

.import-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
}

.secondary-button,
.primary-button {
  border: none;
  border-radius: 5px;
  padding: 8px 12px;
  font: inherit;
  cursor: pointer;
}

.secondary-button {
  background: #f3f4f6;
  color: #111827;
}

.primary-button {
  background: #2563eb;
  color: white;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>