import { defineStore } from 'pinia'

function createInitialNodes() {
  return [
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
}

function createInitialEdges() {
  return [
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
}

export const useWorkflowStore = defineStore('workflow', {
  state: () => ({
    actions: ['Nouveau espace', 'Ajouter script', 'Sauvegarder', 'Executer'],

    scriptGroups: [
      {
        title: 'Detection APD',
        scripts: ['acquisition.py', 'filtre.py', 'fft.py', 'cnn.py'],
      },
      {
        title: 'FPGA JESD204B',
        scripts: ['capture.py', 'analyse.py'],
      },
    ],

    tabs: ['Diagramme', 'Signaux', 'Logs', 'Parametres'],

    nodes: createInitialNodes(),

    edges: createInitialEdges(),
  }),

  actions: {
    addConnection(connection) {
      const edge = {
        ...connection,
        id: `${connection.source}-to-${connection.target}-${Date.now()}`,
        animated: true,
      }

      this.edges.push(edge)
    },

    saveWorkflow() {
      const workflowState = {
        nodes: this.nodes,
        edges: this.edges,
      }

      localStorage.setItem('scientific-workflow-state', JSON.stringify(workflowState))

      alert('Workflow sauvegarde')
    },

    loadWorkflow() {
      const savedState = localStorage.getItem('scientific-workflow-state')

      if (!savedState) {
        return
      }

      const workflowState = JSON.parse(savedState)

      this.nodes = workflowState.nodes
      this.edges = workflowState.edges
    },

    resetWorkflow() {
      this.nodes = createInitialNodes()
      this.edges = createInitialEdges()

      localStorage.removeItem('scientific-workflow-state')
    },
  },
})