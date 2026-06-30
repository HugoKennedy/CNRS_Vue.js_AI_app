<script setup>
import { onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import TopBar from './components/TopBar.vue'
import WorkflowCanvas from './components/WorkflowCanvas.vue'
import { useWorkflowStore } from './stores/workflowStore'

const workflowStore = useWorkflowStore()

workflowStore.loadWorkflow()

onMounted(() => {
  workflowStore.loadScripts()
})

function handleActionClick(action) {
  if (action === 'Sauvegarder') {
    workflowStore.saveWorkflow()
  }

  if (action === 'Nouveau espace') {
    workflowStore.resetWorkflow()
  }

  if (action === 'Ajouter script') {
    workflowStore.loadScripts()
  }

  if (action === 'Executer') {
    alert('Cette action executera bientot le workflow')
  }
}

function handleScriptClick(script) {
  workflowStore.addScriptNode(script)
}
</script>

<template>
  <div class="app-shell">
    <TopBar
      title="Scientific Workflow Studio"
      :actions="workflowStore.actions"
      @action-click="handleActionClick"
    />

    <main class="workspace">
      <Sidebar
        :script-groups="workflowStore.scriptGroups"
        :is-loading="workflowStore.isLoadingScripts"
        :error-message="workflowStore.scriptsError"
        @script-click="handleScriptClick"
      />

      <WorkflowCanvas :tabs="workflowStore.tabs" />
    </main>
  </div>
</template>