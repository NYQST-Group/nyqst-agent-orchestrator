import type { Plugin } from 'vite'
import { appendFileSync } from 'node:fs'
import { resolve } from 'node:path'

/**
 * Vite dev-server plugin that handles POST /api/tour/feedback
 * and appends each entry as a line to .tour-feedback.jsonl
 */
export function tourFeedbackPlugin(): Plugin {
  const feedbackPath = resolve(process.cwd(), '.tour-feedback.jsonl')

  return {
    name: 'tour-feedback',
    configureServer(server) {
      server.middlewares.use('/api/tour/feedback', (req, res, next) => {
        if (req.method !== 'POST') {
          next()
          return
        }

        let body = ''
        req.on('data', (chunk: Buffer) => {
          body += chunk.toString()
        })
        req.on('end', () => {
          try {
            const parsed = JSON.parse(body)
            const line = JSON.stringify({
              ...parsed,
              timestamp: parsed.timestamp || new Date().toISOString(),
            })
            appendFileSync(feedbackPath, line + '\n')
            res.writeHead(200, { 'Content-Type': 'application/json' })
            res.end(JSON.stringify({ ok: true }))
          } catch {
            res.writeHead(400, { 'Content-Type': 'application/json' })
            res.end(JSON.stringify({ error: 'Invalid JSON' }))
          }
        })
      })
    },
  }
}
