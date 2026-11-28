import assert from 'node:assert/strict'
import { existsSync, mkdirSync, readFileSync, rmdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { nativeStatus, reader, sha } from '../egyptian-gods/heka-01/study.mjs'
import { controllerFactory } from '../comparative-tests/workflow-controller/controller.mjs'
import { bindHost, child, fixture, gitRunner, loadJSON, observe, saveJSON } from '../comparative-tests/workflow-controller/restart/fixture.mjs'
import { reservations } from '../comparative-tests/workflow-controller/restart/reservation.mjs'

const here = fileURLToPath(new URL('.', import.meta.url))
const heka = fileURLToPath(new URL('../egyptian-gods/heka-01/bridge.mjs', import.meta.url))
const canary = loadJSON(new URL('../comparative-tests/workflow-controller/canary.json', import.meta.url))
const freeze = loadJSON(join(here, 'freeze.json'))
const hash = value => sha(JSON.stringify(value))

async function authorityProbe(input, directory, proposal, spec, caseFile, ledger) {
  // These controller-interface controls have their own lane and a dry writer.
  const proof = reader('probe', ledger, caseFile)
  saveJSON(join(directory, 'initial-proof.json'), proof)
  const host = bindHost(canary.template, spec, false)
  const authority = input.scenario
  if (authority === 'conflicting-grants') host.grants.push({ ...host.grants[0], id: 'grant-duplicate' })
  if (authority === 'stale-receipt') host.receipts[0].revision = spec.commits.competing
  if (authority === 'conflicting-receipts') host.receipts.push({ ...host.receipts[0], id: 'receipt-conflict' })
  if (authority === 'wrong-action') proposal = { ...proposal, action: 'merge' }
  let attempts = 0
  const gate = create({ readState: () => host, writeCanary() {
    attempts++
    throw new Error('Out-of-scope request reached the dry writer')
  } })
  const result = gate.run(proposal)
  return { proof: nativeStatus(proof), recheck: null, authority, code: result.verdict.code,
    decision: result.verdict.decision, execution: result.execution, attempts, writes: 0, competingWrites: 0,
    proposal, scopedHost: host, controller: result, pid: process.pid }
}

function attestBinding(binding, proof, input, target, admission) {
  if (!binding) return null
  const expected = { schema: 'heka-proof-binding-v1', readerPin: freeze.reader,
    question: input.question, obligation: input.obligation,
    snapshot: hash(proof.snapshot), proof: hash(proof.answer), target }
  return hash(binding) === hash(expected) &&
    (admission?.decision !== 'allow' || admission.receiptIds.includes('heka-' + hash(binding)))
}

function disposition(trace) {
  if (['reservation_indeterminate','reservation_unavailable'].includes(trace.code)) return 'missing_evidence'
  if (['completed','failed','indeterminate'].includes(trace.execution)) return 'allow'
  return 'withhold'
}

const [inputPath, gatePath, outputPath] = process.argv.slice(2)
assert(inputPath && gatePath && outputPath, 'Usage: node run.mjs <sealed inputs> <pinned B-Tests gate> <new output>')
const upstream = resolve(gatePath)
const output = resolve(outputPath)
const input = loadJSON(inputPath)
assert.equal(input.schema, 'greek-sprint-packet-v1')
assert.equal(sha(readFileSync(inputPath)), freeze.packets[input.draw].inputs)
assert.equal(sha(readFileSync(upstream)), freeze.upstream_gate_sha256)
for (const [path, digest] of Object.entries(freeze.dependencies)) {
  assert.equal(sha(readFileSync(new URL('../../' + path, import.meta.url))), digest)
}
mkdirSync(output)
const create = await controllerFactory(upstream)
const rows = []
for (const item of input.cases) {
  assert.match(item.id, /^GREEK-(ATHENA|HERMES|HEPHAESTUS)-[DF]-\d\d$/)
  const directory = join(output, item.id)
  mkdirSync(directory)
  const caseFile = join(directory, 'case.json')
  saveJSON(caseFile, item)
  const spec = fixture(directory, ['initial','intended','competing'])
  const git = gitRunner(spec.repo, join(directory, 'driver-git.stdout'))
  const ledger = join(directory, 'ledger')
  const storePath = join(directory, 'store')
  mkdirSync(storePath)
  const store = reservations(storePath, 'record-canary:' + spec.commits.initial)
  if (item.scenario === 'unavailable-store') rmdirSync(storePath)
  reader('prepare', ledger, caseFile)
  const count = item.scenario.startsWith('restart-') ? 2 : 1
  const phases = []
  for (let phase = 1; phase <= count; phase++) {
    const label = 'phase-' + phase
    const lane = join(directory, label)
    mkdirSync(lane)
    const before = observe(git, spec)
    let trace
    if (item.lane === 'controller') {
      trace = await authorityProbe(item, lane, { action: 'record-canary', revision: spec.commits.initial },
        spec, caseFile, ledger)
    } else {
      assert.equal(item.lane, 'bridge')
      const authority = { 'missing-grant': 'absent', 'advice-only': 'advice' }[item.scenario] ?? 'grant'
      const proc = await child(heka, { spec, upstream, lane, ledger, caseFile, storePath,
        phase, authority, readerPin: freeze.reader }, directory, label)
      const receipt = existsSync(proc.result)
      if (receipt && proc.code === 0 && !proc.signal) {
        trace = loadJSON(proc.result)
        assert.equal(trace.pid, proc.pid)
      } else if (proc.code === 74 && !proc.signal && !receipt &&
                 item.scenario === 'restart-interrupted' && phase === 1) {
        trace = { ...loadJSON(join(lane, 'pre-interruption.json')),
          code: 'interrupted', execution: 'indeterminate', pid: proc.pid }
      } else {
        trace = { pid: proc.pid, execution_error: { code: proc.code, signal: proc.signal, receipt } }
      }
      trace.process = { code: proc.code, signal: proc.signal, receipt }
      if (!trace.execution_error) {
        trace.decision = disposition(trace)
        const proof = loadJSON(join(lane, 'initial-proof.json'))
        trace.binding_attested = attestBinding(trace.binding, proof, item, {
          action: 'record-canary', ref: spec.ref, revision: spec.commits.initial,
          intended: spec.commits.intended, namespace: storePath,
        }, trace.admission)
      }
    }
    const readback = observe(git, spec)
    phases.push({ ...trace, before, readback, ref: readback.ref, store: store.inspect() })
  }
  git('bundle', 'create', join(directory, 'fixture.bundle'), '--all')
  rows.push({ id: item.id, set: item.set, lane: item.lane, phases })
}
saveJSON(join(output, 'run.json'), {
  draw: input.draw, packet_sha256: sha(readFileSync(inputPath)), candidate: freeze.baseline, cases: rows,
})
