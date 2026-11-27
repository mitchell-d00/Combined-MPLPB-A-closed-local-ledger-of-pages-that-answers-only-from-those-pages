import assert from 'node:assert/strict'
import { existsSync, mkdirSync, realpathSync, readFileSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { child, fixture, gitRunner, loadJSON, observe, saveJSON } from './fixture.mjs'
import { reservations } from './reservation.mjs'

const [gatePath, output] = process.argv.slice(2)
assert(gatePath && output, 'Usage: node durable-run.mjs <pinned upstream index.mjs> <new output dir>')
const root = resolve(output)
const upstream = realpathSync(gatePath)
mkdirSync(root)
const { fields, scenarios } = loadJSON(new URL('candidate.json', import.meta.url))
const { markers } = loadJSON(new URL('baseline.json', import.meta.url))
const { template } = loadJSON(new URL('../canary.json', import.meta.url))
const entry = fileURLToPath(new URL('durable-worker.mjs', import.meta.url))
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b)
const rows = []
for (const scenario of scenarios) {
  const directory = join(root, scenario.id)
  mkdirSync(directory)
  const spec = fixture(directory, markers)
  const git = gitRunner(spec.repo, join(directory, 'driver-git.stdout'))
  const storePath = join(directory, 'store')
  if (scenario.mode === 'unavailable') writeFileSync(storePath, 'fixture: path is a file\n')
  else mkdirSync(storePath)
  const store = reservations(storePath, 'record-canary:' + spec.commits.initial)
  const matchesRef = (actual, name) => actual.oid === spec.commits[name] && actual.marker === name

  async function phase(plan, index) {
    const before = observe(git, spec)
    const proc = await child(entry, { spec, template, upstream, options: plan.options, storePath,
      lane: index + 1 }, directory, 'phase-' + (index + 1))
    const after = observe(git, spec)
    const resultExists = existsSync(proc.result)
    const raw = resultExists ? loadJSON(proc.result) : null
    const receipt = { ...proc, result: proc.result.split('/').at(-1), resultExists }
    const refCorrect = !plan.ref || matchesRef(after, plan.ref)
    if (plan.expectCrash) {
      const file = proc.result + '.events'
      const events = existsSync(file) ? readFileSync(file, 'utf8').trim().split('\n') : []
      const outcome = { exit: proc.code, events, attempts: events.filter(e => e === 'writer_attempt').length,
        writes: Number(before.oid !== after.oid && matchesRef(after, 'intended')), store: store.inspect() }
      return { expectCrash: plan.expectCrash, process: receipt, before, after, outcome,
        passed: !resultExists && !proc.signal && same(outcome, plan.expectCrash) && refCorrect }
    }
    const outcome = raw ? fields.map(field => (raw.verdict[field] ?? raw[field])) : null
    return { expect: plan.expect, process: receipt, before, after, outcome, raw,
      passed: proc.code === 0 && Boolean(raw) && raw.pid === proc.pid && refCorrect &&
        (scenario.mode === 'race' || (same(outcome, plan.expect) && raw.ref.oid === after.oid)) }
  }

  let phases
  let raceMatched = true
  if (scenario.mode === 'race') {
    phases = await Promise.all(scenario.phases.map(phase))
    raceMatched = same(phases.map(p => JSON.stringify(p.outcome)).sort(),
      scenario.phases.map(p => JSON.stringify(p.expect)).sort()) &&
      phases.every(p => p.raw?.initialAdmission.decision === 'allow')
  } else {
    phases = []
    for (const [i, plan] of scenario.phases.entries()) phases.push(await phase(plan, i))
  }
  const final = observe(git, spec)
  const fresh = phases.length === new Set(phases.map(p => p.process.pid)).size
  const continuous = scenario.mode === 'race' || phases.every((p, i) => i === 0 || phases[i - 1].after.oid === p.before.oid)
  git('bundle', 'create', join(directory, 'fixture.bundle'), '--all')
  git('bundle', 'verify', join(directory, 'fixture.bundle'))
  rows.push({ id: scenario.id, mode: scenario.mode, fresh, continuous, final, phases,
    passed: fresh && continuous && raceMatched && matchesRef(final, scenario.ref) &&
      phases.every(result => result.passed) })
}
saveJSON(join(root, 'candidate-results.json'), { cases: rows.length,
  passed: rows.filter(row => row.passed).length, rows })
console.log('Candidate:', rows.filter(row => row.passed).length, '/', rows.length)
if (rows.some(row => !row.passed)) process.exitCode = 1
