import assert from 'node:assert/strict'
import { realpathSync, mkdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { child, fixture, gitRunner, loadJSON, observe, saveJSON } from './fixture.mjs'

const [gatePath, output] = process.argv.slice(2)
assert(gatePath && output, 'Usage: node baseline-run.mjs <pinned upstream index.mjs> <new output dir>')
const upstream = realpathSync(gatePath)
const root = resolve(output)
mkdirSync(root)
const { scenarios, markers } = loadJSON(new URL('baseline.json', import.meta.url))
const { template } = loadJSON(new URL('../canary.json', import.meta.url))
const entry = fileURLToPath(new URL('baseline-worker.mjs', import.meta.url))
const rows = []
for (const scenario of scenarios) {
  const directory = join(root, scenario.id)
  mkdirSync(directory)
  const spec = fixture(directory, markers)
  const git = gitRunner(spec.repo, join(directory, 'driver-git.stdout'))
  const phases = []
  for (const [index, expect] of scenario.expect.entries()) {
    const before = observe(git, spec)
    const proc = await child(entry, {
      spec, template, upstream, hostUsed: index === 1 && scenario.host_retains,
      competing: index === 0 && scenario.competing,
    }, directory, 'phase-' + (index + 1))
    const after = observe(git, spec)
    if (proc.code !== 0) {
      phases.push({ process: proc, before, after, executionProblem: true, passed: false })
      break
    }
    const raw = loadJSON(proc.result)
    const { decision, code } = raw.verdict
    const { execution, attempts, writes, competingWrites, hostUsed } = raw
    const outcome = { decision, code, execution, attempts, writes, competingWrites,
      ref: after.ref, hostUsed, reserved: raw.subsequent.code === 'duplicate_request' }
    const passed = Object.keys(expect).every(key => expect[key] === outcome[key]) &&
      after.marker === expect.ref && after.oid === spec.commits[expect.ref] &&
      raw.ref.oid === after.oid && proc.pid === raw.pid
    phases.push({ expect, outcome, before, after, process: { ...proc, result: proc.result.split('/').at(-1) },
      raw, passed })
  }
  const fresh = phases.length === 2 && phases[0].process.pid !== phases[1].process.pid
  const sameRequest = phases.length === 2 &&
    JSON.stringify(phases[0].raw?.proposal) === JSON.stringify(phases[1].raw?.proposal)
  const continuous = phases.length === 2 && phases[0].after.oid === phases[1].before.oid
  git('bundle', 'create', join(directory, 'fixture.bundle'), '--all')
  git('bundle', 'verify', join(directory, 'fixture.bundle'))
  rows.push({ id: scenario.id, fresh, sameRequest, continuous, phases,
    passed: fresh && sameRequest && continuous && phases.every(phase => phase.passed) })
}
saveJSON(join(root, 'baseline-results.json'), { cases: rows.length,
  passed: rows.filter(row => row.passed).length, rows })
console.log('Baseline:', rows.filter(row => row.passed).length, '/', rows.length)
if (rows.some(row => !row.passed)) process.exitCode = 1
