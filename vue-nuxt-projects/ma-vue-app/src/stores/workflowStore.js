import { defineStore } from 'pinia'

const STORAGE_KEY = 'scientific-workflow-state-empty-start'

function createInitialNodes() {
  return []
}

function createInitialEdges() {
  return []
}

function parseParameterValue(value) {
  if (value === '') {
    return ''
  }

  const numberValue = Number(value)

  if (!Number.isNaN(numberValue) && value.trim() !== '') {
    return numberValue
  }

  return value
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
    actions: ['Reinitialiser', 'Ajouter script', 'Sauvegarder', 'Executer'],

    scriptGroups: [],
    scripts: [],
    isLoadingScripts: false,
    scriptsError: '',

    tabs: ['Diagramme', 'Signaux', 'Logs', 'Parametres'],
    activeTab: 'Diagramme',

    nodes: createInitialNodes(),
    edges: createInitialEdges(),
    nextNodeIndex: 0,

    selectedNodeId: '',

    isRunning: false,
    executionResult: null,
    executionError: '',
    executionLogs: ['Aucune execution lancee pour le moment.'],
  }),

  getters: {
    selectedNode(state) {
      return state.nodes.find((node) => node.id === state.selectedNodeId) || null
    },
  },

  actions: {
    setActiveTab(tab) {
      this.activeTab = tab
    },

    selectNode(nodeId) {
      this.selectedNodeId = nodeId
    },

    updateSelectedNodeParameter(parameterName, parameterValue) {
      const node = this.selectedNode

      if (!node) {
        return
      }

      node.data.parameters = {
        ...node.data.parameters,
        [parameterName]: parseParameterValue(parameterValue),
      }
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
      this.selectedNodeId = nodeId
      this.activeTab = 'Diagramme'
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
        selectedNodeId: this.selectedNodeId,
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(workflowState))

      alert('Workflow sauvegarde')
    },

    loadWorkflow() {
      const savedState = localStorage.getItem(STORAGE_KEY)

      if (!savedState) {
        this.nodes = createInitialNodes()
        this.edges = createInitialEdges()
        this.nextNodeIndex = 0
        this.selectedNodeId = ''
        return
      }

      try {
        const workflowState = JSON.parse(savedState)

        this.nodes = workflowState.nodes || createInitialNodes()
        this.edges = workflowState.edges || createInitialEdges()
        this.nextNodeIndex = workflowState.nextNodeIndex || 0
        this.selectedNodeId = workflowState.selectedNodeId || ''
      } catch (error) {
        console.error('Erreur pendant le chargement du workflow', error)
        localStorage.removeItem(STORAGE_KEY)

        this.nodes = createInitialNodes()
        this.edges = createInitialEdges()
        this.nextNodeIndex = 0
        this.selectedNodeId = ''
      }
    },

    resetWorkflow() {
      this.nodes = createInitialNodes()
      this.edges = createInitialEdges()
      this.nextNodeIndex = 0
      this.selectedNodeId = ''
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

        const result = await response.json().catch(() => null)

        if (!response.ok) {
          throw new Error(
            result?.details || result?.message || `Erreur HTTP ${response.status}`,
          )
        }

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