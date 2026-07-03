<script setup>
import { computed, onMounted, ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import TopBar from './components/TopBar.vue'
import WorkflowCanvas from './components/WorkflowCanvas.vue'
import { useWorkflowStore } from './stores/workflowStore'

const workflowStore = useWorkflowStore()

const NEW_CATEGORY_VALUE = '__new_category__'

const isImportModalOpen = ref(false)
const selectedFile = ref(null)
const selectedGroup = ref(NEW_CATEGORY_VALUE)
const newCategoryName = ref('')
const isImporting = ref(false)

workflowStore.loadWorkflow()

onMounted(async () => {
  await workflowStore.loadScripts()
  resetSelectedCategory()
})

const selectedFileName = computed(() => selectedFile.value?.name || '')

const categoryOptions = computed(() => {
  const categories = new Set()

  for (const group of workflowStore.scriptGroups) {
    if (group.title && group.scripts && group.scripts.length > 0) {
      categories.add(group.title)
    }
  }

  return Array.from(categories)
})

const isNewCategorySelected = computed(
  () => selectedGroup.value === NEW_CATEGORY_VALUE,
)

const importCategory = computed(() => {
  if (isNewCategorySelected.value) {
    return newCategoryName.value.trim()
  }

  return selectedGroup.value
})

function resetSelectedCategory() {
  if (categoryOptions.value.length === 0) {
    selectedGroup.value = NEW_CATEGORY_VALUE
    return
  }

  if (
    !selectedGroup.value ||
    selectedGroup.value === NEW_CATEGORY_VALUE ||
    !categoryOptions.value.includes(selectedGroup.value)
  ) {
    selectedGroup.value = categoryOptions.value[0]
  }
}

async function openImportModal() {
  selectedFile.value = null
  newCategoryName.value = ''
  workflowStore.importScriptStatus = ''
  workflowStore.importScriptError = ''

  await workflowStore.loadScripts()
  resetSelectedCategory()

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
  workflowStore.importScriptStatus = ''
  workflowStore.importScriptError = ''

  if (isNewCategorySelected.value && !newCategoryName.value.trim()) {
    workflowStore.importScriptError = 'Le nom de la nouvelle categorie est vide.'
    return
  }

  isImporting.value = true

  const success = await workflowStore.importPythonScript({
    file: selectedFile.value,
    group: importCategory.value,
  })

  isImporting.value = false

  if (success) {
    selectedFile.value = null
    newCategoryName.value = ''

    await workflowStore.loadScripts()
    resetSelectedCategory()

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

function handleGroupDelete(groupTitle) {
  workflowStore.deleteScriptGroup(groupTitle)
}
</script>

<template>
  <div class="app-shell">
    <TopBar
      title="SID4SIM"
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
        @group-delete="handleGroupDelete"
      />

      <WorkflowCanvas :tabs="workflowStore.tabs" />
    </main>

    <div
      v-if="workflowStore.isRunning"
      class="execution-status-bar"
    >
      <div class="execution-status-content">
        <span class="execution-spinner" />

        <span>
          Execution en cours
        </span>
      </div>

      <div class="execution-progress-track">
        <div class="execution-progress-fill" />
      </div>
    </div>

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
              <option
                v-for="category in categoryOptions"
                :key="category"
                :value="category"
              >
                {{ category }}
              </option>

              <option :value="NEW_CATEGORY_VALUE">
                Nouvelle categorie
              </option>
            </select>
          </label>

          <label
            v-if="isNewCategorySelected"
            class="form-label"
          >
            Nom de la nouvelle categorie

            <input
              v-model="newCategoryName"
              type="text"
              class="category-input"
              placeholder="Ex : Filtre RC"
            />
          </label>

          <p class="modal-help">
            Les categories affichees viennent uniquement des scripts deja
            presents dans ThinkML. Si aucun script n existe, tu dois creer une
            nouvelle categorie avec ton premier script.
          </p>

          <p class="modal-help secondary-help">
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
  width: 480px;
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
.category-select,
.category-input {
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

.secondary-help {
  margin-top: 10px;
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

.secondary-button:hover {
  background: #e5e7eb;
}

.primary-button {
  background: #2563eb;
  color: white;
}

.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.execution-status-bar {
  position: fixed;
  left: 16px;
  right: 16px;
  bottom: 16px;
  z-index: 80;
  overflow: hidden;
  border: 1px solid #86efac;
  border-radius: 8px;
  background: #f0fdf4;
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.18);
}

.execution-status-content {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px;
  color: #14532d;
  font-weight: 700;
}

.execution-spinner {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  border: 3px solid #bbf7d0;
  border-top-color: #16a34a;
  border-radius: 999px;
  animation: spin 0.75s linear infinite;
}

.execution-progress-track {
  height: 6px;
  overflow: hidden;
  background: #dcfce7;
}

.execution-progress-fill {
  width: 45%;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #22c55e, #16a34a, #15803d);
  animation: progress-slide 1.25s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes progress-slide {
  0% {
    transform: translateX(-120%);
  }

  50% {
    transform: translateX(80%);
  }

  100% {
    transform: translateX(240%);
  }
}
</style>