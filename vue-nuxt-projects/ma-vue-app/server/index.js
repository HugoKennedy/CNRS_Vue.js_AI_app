import express from 'express'
import { readFile } from 'node:fs/promises'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawn } from 'node:child_process'

const app = express()
const port = 3001

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const projectRoot = join(__dirname, '..')

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

function runPythonScript(scriptFile, payload) {
  return new Promise((resolve, reject) => {
    const scriptPath = join(projectRoot, 'scripts', scriptFile)
    const pythonProcess = spawn('python', [scriptPath])

    let stdout = ''
    let stderr = ''

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    pythonProcess.on('error', (error) => {
      reject(
        new Error(
          `Impossible de lancer Python. Verifie que Python est installe et accessible avec la commande "python". Detail : ${error.message}`,
        ),
      )
    })

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Erreur dans ${scriptFile} : ${stderr}`))
        return
      }

      try {
        resolve(JSON.parse(stdout))
      } catch (error) {
        reject(
          new Error(
            `Le script ${scriptFile} n a pas renvoye un JSON valide. Sortie recue : ${stdout}`,
          ),
        )
      }
    })

    pythonProcess.stdin.write(JSON.stringify(payload))
    pythonProcess.stdin.end()
  })
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

app.post('/api/run', async (req, res) => {
  const { nodes = [], edges = [] } = req.body

  if (!Array.isArray(nodes) || !Array.isArray(edges)) {
    return res.status(400).json({
      status: 'error',
      message: 'Invalid workflow payload',
    })
  }

  try {
    const orderedNodes = buildExecutionOrder(nodes, edges)
    const logs = ['Workflow recu par le serveur Node.']
    let data = {}

    for (const node of orderedNodes) {
      const scriptFile = node.data?.file
      const parameters = node.data?.parameters || {}

      if (!scriptFile) {
        logs.push(`Bloc ignore : ${node.id}`)
        continue
      }

      logs.push(`Execution de ${scriptFile}...`)

      data = await runPythonScript(scriptFile, {
        nodeId: node.id,
        file: scriptFile,
        parameters,
        data,
      })

      logs.push(`${scriptFile} termine.`)
    }

    const executionOrder = orderedNodes.map((node) => node.data?.file || node.id)

    res.json({
      status: 'ok',
      message: 'Workflow execute avec scripts Python fictifs',
      nodeCount: nodes.length,
      edgeCount: edges.length,
      executionOrder,
      logs,
      simulatedOutputs: data,
    })
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: 'Erreur pendant l execution Python',
      details: error.message,
      logs: [`Erreur : ${error.message}`],
    })
  }
})

app.listen(port, () => {
  console.log(`Scientific Workflow API running at http://localhost:${port}`)
})