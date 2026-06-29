<script setup>
import TopBar from './components/TopBar.vue'
import Sidebar from './components/Sidebar.vue'
import WorkflowCanvas from './components/WorkflowCanvas.vue'

const actions = ['Nouveau espace', 'Ajouter script', 'Sauvegarder', 'Executer']

const scriptGroups = [
  {
    title: 'Detection APD',
    scripts: ['acquisition.py', 'filtre.py', 'fft.py', 'cnn.py'],
  },
  {
    title: 'FPGA JESD204B',
    scripts: ['capture.py', 'analyse.py'],
  },
]

const tabs = ['Diagramme', 'Signaux', 'Logs', 'Parametres']

const workflowNodes = [
  {
    id: 'acquisition',
    file: 'acquisition.py',
    lines: ['Sortie : signal'],
    x: 80,
    y: 150,
  },
  {
    id: 'fft',
    file: 'fft.py',
    lines: ['Entree : signal', 'Sortie : spectre'],
    x: 370,
    y: 150,
  },
  {
    id: 'cnn',
    file: 'cnn.py',
    lines: ['Entree : spectre', 'Sortie : classes'],
    x: 660,
    y: 150,
  },
]

const workflowConnections = [
  { id: 'acquisition-to-fft', x: 250, y: 195, width: 120 },
  { id: 'fft-to-cnn', x: 540, y: 195, width: 120 },
]
</script>

<template>
  <div class="app-shell">
    <TopBar title="Scientific Workflow Studio" :actions="actions" />

    <main class="workspace">
      <Sidebar :script-groups="scriptGroups" />

      <WorkflowCanvas
        :tabs="tabs"
        :nodes="workflowNodes"
        :connections="workflowConnections"
      />
    </main>
  </div>
</template>