import { defineStore } from 'pinia'

const STORAGE_KEY = 'scientific-workflow-state'

function createInitialNodes() {
  return [
    {
      id: 'acquisition',
      type: 'scriptNode',
      position: { x: 80, y: 150 },
      data: {
        file: 'acquisition.py',
        label: 'Acquisition APD',
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
        label: 'Transformee FFT',
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
        label: 'Classification CNN',
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

function cleanNode(node) {
  return {
    id: node.id,
    type: node.type,
    position: {
      x: node.position.x,
      y: node.position.y,
    },
    data: {
      file: node.data.file,
      label: node.data.label,
      description: node.data.description,
      inputs: node.data.inputs || [],
      outputs: node.data.outputs || [],
      parameters: node.data.parameters || {},
    },
  }
}

function cleanEdge(edge) {
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    sourceHandle: edge.sourceHandle,
    targetHandle: edge.targetHandle,
    animated: edge.animated || true,
  }
}

export const useWorkflowStore = defineStore('workflow', {
  state: () => ({
    actions: ['Nouveau espace', 'Ajouter script', 'Sauvegarder', 'Executer'],

    scriptGroups: [],
    scripts: [],
    isLoadingScripts: false,
    scriptsError: '',

    tabs: ['Diagramme', 'Signaux', 'Logs', 'Parametres'],
    activeTab: 'Diagramme',

    nodes: createInitialNodes(),
    edges: createInitialEdges(),
    nextNodeIndex: 1,

    isRunning: false,
    executionResult: null,
    executionError: '',
    executionLogs: ['Aucune execution lancee pour le moment.'],
  }),

  actions: {
    setActiveTab(tab) {
      this.activeTab = tab
    },

    async loadScripts() {
      this.isLoadingScripts = true
      this.scriptsError = ''

      try {
        const response = await fetch('/api/scripts')

        if (!response.ok) {
          throw new Error(`Erreur HTTP ${response.status}`)
        }

        const data = await response.json()

        this.scripts = data.scripts
        this.scriptGroups = data.groups
      } catch (error) {
        this.scriptsError = error.message
        this.scripts = []
        this.scriptGroups = []
      } finally {
        this.isLoadingScripts = false
      }
    },

    addScriptNode(script) {
      const nodeId = `${script.id}-${Date.now()}`
      const offset = this.nextNodeIndex * 35

      const node = {
        id: nodeId,
        type: 'scriptNode',
        position: {
          x: 120 + offset,
          y: 100 + offset,
        },
        data: {
          file: script.file,
          label: script.label,
          description: script.description,
          inputs: script.inputs || [],
          outputs: script.outputs || [],
          parameters: script.parameters || {},
        },
      }

      this.nodes.push(node)
      this.nextNodeIndex += 1
    },

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
        nodes: this.nodes.map(cleanNode),
        edges: this.edges.map(cleanEdge),
        nextNodeIndex: this.nextNodeIndex,
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(workflowState))

      alert('Workflow sauvegarde')
    },

    loadWorkflow() {
      const savedState = localStorage.getItem(STORAGE_KEY)

      if (!savedState) {
        return
      }

      try {
        const workflowState = JSON.parse(savedState)

        this.nodes = workflowState.nodes || createInitialNodes()
        this.edges = workflowState.edges || createInitialEdges()
        this.nextNodeIndex = workflowState.nextNodeIndex || 1
      } catch (error) {
        console.error('Erreur pendant le chargement du workflow', error)
        localStorage.removeItem(STORAGE_KEY)
      }
    },

    resetWorkflow() {
      this.nodes = createInitialNodes()
      this.edges = createInitialEdges()
      this.nextNodeIndex = 1
      this.executionResult = null
      this.executionError = ''
      this.executionLogs = ['Aucune execution lancee pour le moment.']
      this.activeTab = 'Diagramme'

      localStorage.removeItem(STORAGE_KEY)
    },

    async runWorkflow() {
      this.isRunning = true
      this.executionError = ''
      this.executionLogs = ['Envoi du workflow au serveur...']
      this.activeTab = 'Logs'

      try {
        const payload = {
          nodes: this.nodes.map(cleanNode),
          edges: this.edges.map(cleanEdge),
        }

        const response = await fetch('/api/run', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        })

        if (!response.ok) {
          throw new Error(`Erreur HTTP ${response.status}`)
        }

        const result = await response.json()

        this.executionResult = result
        this.executionLogs = result.logs || ['Execution terminee.']
      } catch (error) {
        this.executionError = error.message
        this.executionLogs = [`Erreur pendant l execution : ${error.message}`]
      } finally {
        this.isRunning = false
      }
    },
  },
})