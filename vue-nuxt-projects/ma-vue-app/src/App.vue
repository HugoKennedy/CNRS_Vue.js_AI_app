<script setup>
import Sidebar from './components/Sidebar.vue'
import TopBar from './components/TopBar.vue'
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
    type: 'scriptNode',
    position: { x: 80, y: 150 },
    data: {
      file: 'acquisition.py',
      inputs: [],
      outputs: ['signal'],
    },
  },
  {
    id: 'fft',
    type: 'scriptNode',
    position: { x: 370, y: 150 },
    data: {
      file: 'fft.py',
      inputs: ['signal'],
      outputs: ['spectre'],
    },
  },
  {
    id: 'cnn',
    type: 'scriptNode',
    position: { x: 660, y: 150 },
    data: {
      file: 'cnn.py',
      inputs: ['spectre'],
      outputs: ['classes'],
    },
  },
]

const workflowEdges = [
  {
    id: 'acquisition-to-fft',
    source: 'acquisition',
    target: 'fft',
    animated: true,
  },
  {
    id: 'fft-to-cnn',
    source: 'fft',
    target: 'cnn',
    animated: true,
  },
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
        :edges="workflowEdges"
      />
    </main>
  </div>
</template>