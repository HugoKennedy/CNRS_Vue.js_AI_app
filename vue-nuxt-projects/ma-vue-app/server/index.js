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

app.listen(port, () => {
  console.log(`Scientific Workflow API running at http://localhost:${port}`)
})