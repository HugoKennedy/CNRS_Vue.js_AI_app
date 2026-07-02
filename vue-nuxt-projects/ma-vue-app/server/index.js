import express from 'express'
import { access, readFile, rename, unlink, writeFile } from 'node:fs/promises'
import { basename, dirname, extname, join, parse } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawn } from 'node:child_process'

const app = express()
const port = 3001

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const projectRoot = join(__dirname, '..')
const scriptsDirectory = join(projectRoot, 'scripts')
const scriptsJsonPath = join(__dirname, 'scripts.json')

const probeData = {
  time: [0, 1, 2, 3],
  signal: [0, 0.5, 1, 0.4],
  signal_filtre: [0, 0.4, 0.7, 0.5],
  frequencies: [0, 1, 2, 3],
  spectre: [12, 8, 3, 1],
  raw_data: [0.1, 0.3, 0.2, 0.5],
}

app.use(express.json({ limit: '2mb' }))

async function readScripts() {
  const scriptsContent = await readFile(scriptsJsonPath, 'utf8')
  return JSON.parse(scriptsContent)
}

async function writeScripts(scripts) {
  await writeFile(scriptsJsonPath, JSON.stringify(scripts, null, 2), 'utf8')
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
    const scriptPath = join(scriptsDirectory, scriptFile)
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
        const output = JSON.parse(stdout)
        delete output.__thinkml_parameters
        delete output.__thinkml_description
        delete output.__thinkml_label

        resolve(output)
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

function validatePythonScriptContract(scriptPath, scriptFile) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python', [scriptPath])

    let stdout = ''
    let stderr = ''
    let isSettled = false

    const timeout = setTimeout(() => {
      if (isSettled) {
        return
      }

      isSettled = true
      pythonProcess.kill()

      reject(
        new Error(
          `Le script ${scriptFile} ne repond pas assez vite au test JSON.`,
        ),
      )
    }, 4000)

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    pythonProcess.on('error', (error) => {
      if (isSettled) {
        return
      }

      isSettled = true
      clearTimeout(timeout)

      reject(
        new Error(
          `Impossible de lancer Python. Verifie que Python est installe et accessible avec la commande "python". Detail : ${error.message}`,
        ),
      )
    })

    pythonProcess.on('close', (code) => {
      if (isSettled) {
        return
      }

      isSettled = true
      clearTimeout(timeout)

      if (code !== 0) {
        reject(
          new Error(
            `Le script ${scriptFile} a echoue pendant le test JSON. Detail : ${stderr}`,
          ),
        )
        return
      }

      try {
        const output = JSON.parse(stdout)

        if (!output || typeof output !== 'object' || Array.isArray(output)) {
          reject(
            new Error(
              `Le script ${scriptFile} doit renvoyer un objet JSON, pas une liste ou une valeur simple.`,
            ),
          )
          return
        }

        resolve(output)
      } catch (error) {
        reject(
          new Error(
            `Le script ${scriptFile} doit afficher un JSON valide avec print(json.dumps(...)). Sortie recue : ${stdout}`,
          ),
        )
      }
    })

    pythonProcess.stdin.write(
      JSON.stringify({
        nodeId: 'validation',
        file: scriptFile,
        parameters: {},
        data: probeData,
      }),
    )

    pythonProcess.stdin.end()
  })
}

function sanitizePythonFileName(fileName) {
  const safeName = basename(fileName).replace(/\s+/g, '_')

  if (extname(safeName).toLowerCase() !== '.py') {
    throw new Error('Le fichier doit avoir l extension .py')
  }

  if (!/^[a-zA-Z0-9._-]+\.py$/.test(safeName)) {
    throw new Error(
      'Le nom du fichier ne doit contenir que lettres, chiffres, points, tirets ou underscores.',
    )
  }

  return safeName
}

function createScriptId(fileName, existingScripts) {
  const baseId = parse(fileName)
    .name.toLowerCase()
    .replace(/[^a-z0-9_-]/g, '_')

  let candidateId = baseId
  let index = 2

  while (existingScripts.some((script) => script.id === candidateId)) {
    candidateId = `${baseId}_${index}`
    index += 1
  }

  return candidateId
}

function inferOutputs(output) {
  const ignoredKeys = ['time', 'frequencies']
  const probeKeys = Object.keys(probeData)

  const visibleKeys = Object.keys(output).filter(
    (key) => !key.startsWith('__thinkml_'),
  )

  const newKeys = visibleKeys.filter(
    (key) => !probeKeys.includes(key) && !ignoredKeys.includes(key),
  )

  if (newKeys.length > 0) {
    return newKeys
  }

  return visibleKeys.filter((key) => !ignoredKeys.includes(key))
}

function inferInputs(group, outputs) {
  if (outputs.includes('signal_apres_resistance')) {
    return ['signal']
  }

  if (
    outputs.includes('signal_sortie') ||
    outputs.includes('tension_condensateur')
  ) {
    return ['signal_apres_resistance']
  }

  if (outputs.includes('gain_approx')) {
    return ['signal_sortie']
  }

  if (group === 'FPGA JESD204B') {
    if (outputs.includes('raw_data')) {
      return []
    }

    return ['raw_data']
  }

  if (outputs.includes('spectre')) {
    return ['signal']
  }

  if (outputs.includes('classes') || outputs.includes('classification_score')) {
    return ['spectre']
  }

  if (outputs.some((output) => output.includes('anomaly'))) {
    return ['signal']
  }

  if (outputs.length === 1 && outputs[0] === 'signal') {
    return []
  }

  if (outputs.some((output) => output.startsWith('signal'))) {
    return ['signal']
  }

  return []
}

function normalizeGroup(group) {
  const cleanedGroup = String(group || '').trim()

  if (!cleanedGroup) {
    throw new Error('La categorie est vide.')
  }

  return cleanedGroup
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

app.post('/api/scripts/import', async (req, res) => {
  let tempScriptPath = ''

  try {
    const { fileName, group, content } = req.body

    if (!fileName || !group || !content) {
      return res.status(400).json({
        status: 'error',
        message: 'fileName, group et content sont obligatoires.',
      })
    }

    const safeFileName = sanitizePythonFileName(fileName)
    const normalizedGroup = normalizeGroup(group)
    const finalScriptPath = join(scriptsDirectory, safeFileName)

    try {
      await access(finalScriptPath)

      return res.status(409).json({
        status: 'error',
        message: `Le fichier ${safeFileName} existe deja dans le dossier scripts.`,
      })
    } catch (error) {
      // Le fichier n existe pas encore, on peut continuer.
    }

    tempScriptPath = join(
      scriptsDirectory,
      `.__candidate_${Date.now()}_${safeFileName}`,
    )

    await writeFile(tempScriptPath, content, 'utf8')

    const validationOutput = await validatePythonScriptContract(
      tempScriptPath,
      safeFileName,
    )

    const scripts = await readScripts()
    const scriptId = createScriptId(safeFileName, scripts)
    const outputs = inferOutputs(validationOutput)
    const inputs = inferInputs(normalizedGroup, outputs)

    const newScript = {
      id: scriptId,
      file: safeFileName,
      label: validationOutput.__thinkml_label || parse(safeFileName).name,
      group: normalizedGroup,
      description:
        validationOutput.__thinkml_description ||
        'Script Python ajoute depuis l interface.',
      inputs,
      outputs,
      parameters: validationOutput.__thinkml_parameters || {},
    }

    await rename(tempScriptPath, finalScriptPath)

    scripts.push(newScript)
    await writeScripts(scripts)

    res.json({
      status: 'ok',
      message: `Script ${safeFileName} ajoute avec succes.`,
      script: newScript,
      validation: {
        outputKeys: Object.keys(validationOutput).filter(
          (key) => !key.startsWith('__thinkml_'),
        ),
      },
    })
  } catch (error) {
    if (tempScriptPath) {
      await unlink(tempScriptPath).catch(() => {})
    }

    res.status(400).json({
      status: 'error',
      message: 'Impossible d ajouter le script.',
      details: error.message,
    })
  }
})

app.delete('/api/scripts/:scriptId', async (req, res) => {
  try {
    const { scriptId } = req.params
    const scripts = await readScripts()
    const scriptToDelete = scripts.find((script) => script.id === scriptId)

    if (!scriptToDelete) {
      return res.status(404).json({
        status: 'error',
        message: 'Script introuvable.',
      })
    }

    const scriptPath = join(scriptsDirectory, scriptToDelete.file)

    await unlink(scriptPath).catch((error) => {
      if (error.code !== 'ENOENT') {
        throw error
      }
    })

    const updatedScripts = scripts.filter((script) => script.id !== scriptId)
    await writeScripts(updatedScripts)

    res.json({
      status: 'ok',
      message: `Script ${scriptToDelete.file} supprime.`,
      script: scriptToDelete,
    })
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: 'Impossible de supprimer le script.',
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
      message: 'Workflow execute avec scripts Python',
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
  console.log(`ThinkML API running at http://localhost:${port}`)
})