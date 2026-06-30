import express from 'express'
import { readFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const app = express()
const port = 3001

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

app.use(express.json())

async function readScripts() {
  const scriptsPath = join(__dirname, 'scripts.json')
  const scriptsContent = await readFile(scriptsPath, 'utf8')

  return JSON.parse(scriptsContent)
}

function groupScriptsByWorkspace(scripts) {
  const groupsByTitle = new Map()

  for (const script of scripts) {
    if (!groupsByTitle.has(script.group)) {
      groupsByTitle.set(script.group, {
        title: script.group,
        scripts: [],
      })
    }

    groupsByTitle.get(script.group).scripts.push(script)
  }

  return Array.from(groupsByTitle.values())
}

function buildExecutionOrder(nodes, edges) {
  const nodeIds = nodes.map((node) => node.id)
  const incomingCount = new Map(nodeIds.map((id) => [id, 0]))
  const outgoing = new Map(nodeIds.map((id) => [id, []]))

  for (const edge of edges) {
    if (!incomingCount.has(edge.target) || !outgoing.has(edge.source)) {
      continue
    }

    incomingCount.set(edge.target, incomingCount.get(edge.target) + 1)
    outgoing.get(edge.source).push(edge.target)
  }

  const queue = nodeIds.filter((id) => incomingCount.get(id) === 0)
  const orderedIds = []

  while (queue.length > 0) {
    const currentId = queue.shift()
    orderedIds.push(currentId)

    for (const targetId of outgoing.get(currentId)) {
      incomingCount.set(targetId, incomingCount.get(targetId) - 1)

      if (incomingCount.get(targetId) === 0) {
        queue.push(targetId)
      }
    }
  }

  if (orderedIds.length !== nodes.length) {
    return nodes
  }

  return orderedIds.map((id) => nodes.find((node) => node.id === id))
}

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'scientific-workflow-api',
    timestamp: new Date().toISOString(),
  })
})

app.get('/api/scripts', async (req, res) => {
  try {
    const scripts = await readScripts()
    const groups = groupScriptsByWorkspace(scripts)

    res.json({
      scripts,
      groups,
    })
  } catch (error) {
    res.status(500).json({
      error: 'Unable to read scripts list',
      details: error.message,
    })
  }
})

app.post('/api/run', (req, res) => {
  const { nodes = [], edges = [] } = req.body

  if (!Array.isArray(nodes) || !Array.isArray(edges)) {
    return res.status(400).json({
      status: 'error',
      message: 'Invalid workflow payload',
    })
  }

  const orderedNodes = buildExecutionOrder(nodes, edges)
  const executionOrder = orderedNodes.map((node) => node.data?.file || node.id)

  const logs = [
    'Workflow recu par le serveur Node.',
    `${nodes.length} bloc(s) detecte(s).`,
    `${edges.length} connexion(s) detectee(s).`,
    `Ordre d execution propose : ${executionOrder.join(' -> ')}`,
    'Execution fictive terminee avec succes.',
  ]

  res.json({
    status: 'ok',
    message: 'Workflow execute en mode simulation',
    nodeCount: nodes.length,
    edgeCount: edges.length,
    executionOrder,
    logs,
    simulatedOutputs: {
      time: [0, 1, 2, 3, 4],
      signal: [0.0, 0.8, 1.0, 0.5, 0.1],
    },
  })
})

app.listen(port, () => {
  console.log(`Scientific Workflow API running at http://localhost:${port}`)
})