/** Disposable lab only. Inputs are operator fixtures with no evaluator dependencies. */
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs'
import { basename, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { controllerFactory } from '../../comparative-tests/workflow-controller/controller.mjs'
import { bindHost, fixture, gitRunner, loadJSON, observe, saveJSON } from '../../comparative-tests/workflow-controller/restart/fixture.mjs'
import { reservations } from '../../comparative-tests/workflow-controller/restart/reservation.mjs'
import { canonical, project, sha } from './projection.mjs'

const lab = fileURLToPath(new URL('.', import.meta.url))
const root = fileURLToPath(new URL('../../../', import.meta.url))
const control = join(root, 'evaluation/comparative-tests/workflow-controller')
const baseline = 'cabcd140ee438b0a63784faa2c0fc4b2a8c54e66'
const action = 'record-canary'
const template = loadJSON(join(control, 'canary.json')).template
const policy = {
  version: 'instruction-record-lab-v1',
  controller: sha(readFileSync(join(control, 'controller.mjs'))),
  contract: sha(readFileSync(join(lab, 'CONTRACT.md'))),
  projection: sha(readFileSync(join(lab, 'projection.mjs'))),
}

function readNative(operation, ledger, input) {
  const args = [join(lab, 'native.py'), operation, ledger, input]
  const env = { PATH: '/nonexistent', PYTHONPATH: root, PYTHONDONTWRITEBYTECODE: '1' }
  const out = execFileSync('/usr/bin/python3', args, { env, timeout: 6000, maxBuffer: 2 * 1024 * 1024 })
  return out.length ? JSON.parse(out) : null
}

function fixtureTarget(directory) {
  const repo = fixture(directory, ['initial', 'intended'])
  const namespace = join(directory, 'store')
  mkdirSync(namespace, { mode: 0o700 })
  return { ...repo, namespace, git: gitRunner(repo.repo, join(directory, 'worker-git.stdout')) }
}

function stage(fixture, bytes) {
  const { git, repo, commits } = fixture
  git('switch', '--quiet', '--detach', commits.intended)
  writeFileSync(join(repo, 'assertion.json'), bytes, { flag: 'wx' })
  git('add', '--', 'assertion.json')
  git('commit', '--quiet', '-m', 'Record attributed source assertion')
  commits.intended = git('rev-parse', 'HEAD')
  git('switch', '--quiet', 'main')
  return {
    repository: realpathSync(repo), namespace: realpathSync(fixture.namespace),
    ref: fixture.ref, old_oid: commits.initial, new_oid: commits.intended,
  }
}

function readback(fixture, capture) {
  const git = gitRunner(fixture.repo, capture)
  const result = observe(git, fixture)
  const record_sha256 = result.marker === 'intended'
    ? (git('cat-file', 'blob', result.oid + ':assertion.json'), sha(readFileSync(capture))) : null
  return { ...result, record_sha256 }
}

function bind(record, raw, target) {
  return {
    schema: 'instruction-record-binding-v1', action, reader: baseline, policy,
    record: sha(canonical(record) + '\n'), proof: sha(canonical(raw.answer)),
    source_revisions: sha(canonical(raw.snapshot)), target,
  }
}

async function runCase(item, directory, create) {
  const path = name => join(directory, name)
  const input = path('input.json')
  const ledger = path('ledger')
  saveJSON(input, item)
  readNative('prepare', ledger, input)
  const fixture = fixtureTarget(directory)
  const before = readback(fixture, path('actual-before.stdout'))
  const key = action + ':' + before.oid
  const store = reservations(fixture.namespace, key)
  assert.equal(store.inspect(), 'unused')
  const trace = { id: item.id, baseline, initial: null, reread: null, before, record: null,
    binding: null, grant: null, authorization: 'not_run', attempts: 0, writes: 0 }
  const receipt = join(fixture.namespace, sha(key), 'outcome.json')

  function report(stage) {
    const after = readback(fixture, path('actual-after.stdout'))
    return { ...trace, stage, after, reservation: store.inspect(),
      durable: existsSync(receipt) ? loadJSON(receipt) : null,
      receipt_sha256: existsSync(receipt) ? sha(readFileSync(receipt)) : null }
  }

  const raw = readNative('probe', ledger, input)
  trace.initial = raw
  const record = project(raw, item.question, baseline)
  if (!record) {
    const code = raw.answer.diagnostic.code
    return report(code === 'interpretation_unsupported' ? 'interpretation'
      : code === 'instruction_attribution_unresolved' ? 'instruction-proof' : 'projection')
  }

  const bytes = canonical(record) + '\n'
  const target = stage(fixture, bytes)
  const binding = bind(record, raw, target)
  Object.assign(trace, { record, binding })
  const state = bindHost(template, fixture, false)
  state.receipts[0].id = 'proof-' + sha(canonical(binding))
  let grantTarget = target
  if (item.scenario === 'wrong-resource') {
    mkdirSync(path('other'))
    const other = fixtureTarget(path('other'))
    grantTarget = stage(other, bytes)
    assert.equal(grantTarget.old_oid, target.old_oid)
    assert.equal(grantTarget.new_oid, target.new_oid)
    assert.equal(grantTarget.ref, target.ref)
  }
  // The disposable host's operator direction supplies (or withholds) an exact
  // grant. Native evidence cannot set this input or the worker's capability.
  const grant = item.scenario === 'absent' ? null : {
    ...state.grants[0], bound: sha(canonical(bind(record, raw, grantTarget))),
  }
  trace.grant = grant
  let current = true
  const authorization = () => grant === null ? 'grant_missing'
    : grant.bound !== sha(canonical(binding)) ? 'grant_binding_mismatch' : 'allowed'
  const proposal = { action, revision: target.old_oid }
  const gate = create({
    readState() {
      const exact = authorization() === 'allowed'
      return { ...state, revision: fixture.git('rev-parse', target.ref),
        receipts: current ? state.receipts : [], grants: exact ? state.grants : [] }
    },
    beforeWrite() {
      if (item.scenario === 'withdraw') readNative('withdraw', ledger, input)
      const fresh = readNative('probe', ledger, input)
      trace.reread = fresh
      const rerecord = project(fresh, item.question, baseline)
      current = rerecord !== null && canonical(bind(rerecord, fresh, target)) === canonical(binding)
    },
    writeCanary(scope) {
      assert.deepEqual(scope, { action, revision: target.old_oid, mode: 'local-canary' })
      assert.equal(authorization(), 'allowed')
      assert(current)
      assert(store.claim())
      trace.attempts++
      fixture.git('update-ref', target.ref, target.new_oid, target.old_oid)
      trace.writes++
      const checked = readback(fixture, path('completion-readback.stdout'))
      assert.equal(checked.oid, target.new_oid)
      assert.equal(checked.marker, 'intended')
      assert.equal(checked.record_sha256, binding.record)
      store.finish('completed', checked)
    },
  })

  trace.admission = gate.evaluate(proposal)
  trace.authorization = authorization()
  if (trace.admission.decision !== 'allow') {
    return report(trace.authorization === 'grant_missing' ? 'authorization'
      : trace.authorization === 'grant_binding_mismatch' ? 'target-binding' : 'controller')
  }
  trace.controller = gate.run(proposal)
  if (!current) {
    trace.authorization = 'evidence_changed'
    return report('final-evidence')
  }
  if (trace.controller.execution !== 'completed') return report('execution')
  return report('completed')
}

const [, , input, upstream, output] = process.argv
assert(input && upstream && output, 'Usage: node run.mjs <sealed packet> <pinned gate> <new output directory>')
const packet = loadJSON(input)
assert(['D', 'F'].includes(packet.draw))
const seal = load => new Map(readFileSync(join(lab, load), 'utf8').trim().split('\n')
  .map(line => line.split('  ').reverse()))
const digests = seal('FREEZE-SHA256SUMS')
assert.equal(sha(readFileSync(input)), digests.get(packet.draw + '-inputs.json'))
assert.equal(packet.cases.length, 8)
for (const [name, hash] of seal('DEPENDENCY-SHA256SUMS')) {
  assert.equal(sha(readFileSync(name === 'upstream-index.mjs' ? upstream : join(root, name))), hash, name)
}
const create = await controllerFactory(upstream)
const directory = resolve(output)
mkdirSync(directory, { mode: 0o700 })
const results = []
for (const item of packet.cases) {
  assert.match(item.id, /^IR01-[DF]-0[1-8]$/)
  assert.equal(item.id, basename(item.id))
  const lane = join(directory, item.id)
  mkdirSync(lane)
  try {
    results.push(await runCase(item, lane, create))
  } catch (error) {
    results.push({ id: item.id, execution_error: error.stack })
  }
  saveJSON(join(lane, 'first.json'), results.at(-1))
}
saveJSON(join(directory, 'run.json'), results)
