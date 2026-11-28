import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { closeSync, existsSync, mkdirSync, mkdtempSync, openSync, readFileSync, realpathSync, rmSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { child, fixture, gitRunner, loadJSON, observe, saveJSON } from '../../comparative-tests/workflow-controller/restart/fixture.mjs'
import { reservations } from '../../comparative-tests/workflow-controller/restart/reservation.mjs'

const lab = fileURLToPath(new URL('.', import.meta.url))
const root = fileURLToPath(new URL('../../../', import.meta.url))
export const sha = bytes => createHash('sha256').update(bytes).digest('hex')
export const markers = ['initial', 'intended', 'competing']

export function reader(operation, ledger, caseFile) {
  // File-backed capture avoids the managed runner's pipe teardown EPERM.
  const capture = mkdtempSync(join(dirname(caseFile), '.reader-'))
  const file = join(capture, 'stdout')
  const fd = openSync(file, 'wx')
  try {
    execFileSync('python3', [join(lab, 'reader.py'), operation, ledger, caseFile], {
      cwd: root, timeout: 6000, stdio: ['ignore', fd, 'inherit'],
      env: { PATH: process.env.PATH, PYTHONPATH: root, PYTHONDONTWRITEBYTECODE: '1' },
    })
    return operation === 'probe' ? loadJSON(file) : undefined
  } finally {
    closeSync(fd)
    rmSync(capture, { recursive: true })
  }
}

export function nativeStatus(raw) {
  return raw.answer.kind === 'supported_answer' && raw.answer.answer_supported === true
    ? 'complete' : raw.answer.diagnostic.code
}

function fixtureAuthority(scenario) {
  if (scenario === 'advice-only') return 'advice'
  if (scenario === 'missing-grant') return 'absent'
  return 'grant'
}

async function run(mode, input, upstream, output) {
  assert(['baseline', 'candidate'].includes(mode))
  const packet = loadJSON(input)
  const lock = loadJSON(join(lab, 'freeze.json'))
  assert.equal(packet.schema, 'heka-packet-v1')
  assert.equal(sha(readFileSync(input)), lock.packets[packet.draw].inputs)
  assert.equal(sha(readFileSync(upstream)), lock.upstream_gate_sha256)
  assert.equal(packet.cases.length, lock.packets[packet.draw].cases)
  assert(mode !== 'baseline' || packet.draw === 'D')
  const rootOutput = resolve(output)
  mkdirSync(rootOutput)
  const results = []
  for (const scenario of packet.cases) {
    assert.match(scenario.id, /^HEKA-[DF]-[0-9]{2}$/)
    const directory = join(rootOutput, scenario.id)
    mkdirSync(directory)
    const caseFile = join(directory, 'case.json')
    saveJSON(caseFile, scenario)
    const spec = fixture(directory, markers)
    const git = gitRunner(spec.repo, join(directory, 'driver-git.stdout'))
    const ledger = join(directory, 'ledger')
    const storePath = join(directory, 'store')
    mkdirSync(storePath)
    reader('prepare', ledger, caseFile)
    const phases = []
    const phasesCount = Number(mode === 'candidate' && scenario.scenario.startsWith('restart-')) + 1
    const store = reservations(storePath, 'record-canary:' + spec.commits.initial)
    if (mode === 'candidate' && scenario.scenario === 'unavailable-store') {
      // An absent path is unavailable to the unchanged reservation store.
      const { rmdirSync } = await import('node:fs')
      rmdirSync(storePath)
    }
    for (let phase = 1; phase <= phasesCount; phase++) {
      const before = observe(git, spec)
      const authority = fixtureAuthority(scenario.scenario)
      const label = 'phase-' + phase
      const lane = join(directory, label)
      mkdirSync(lane)
      let observed
      if (mode === 'baseline') {
        const raw = reader('probe', ledger, caseFile)
        saveJSON(join(lane, 'initial-proof.json'), raw)
        observed = { code: 'bridge_unconnected', proof: nativeStatus(raw), recheck: null, authority,
          execution: 'not_run', attempts: 0, writes: 0, pid: process.pid }
      } else {
        const entry = join(lab, 'bridge.mjs')
        const proc = await child(entry, { spec, upstream, lane, ledger, caseFile, storePath,
          phase, authority, readerPin: lock.reader }, directory, label)
        if (existsSync(proc.result) && proc.code === 0 && !proc.signal) {
          observed = loadJSON(proc.result)
          assert.equal(proc.pid, observed.pid)
        } else if (proc.code === 74 && !proc.signal && !existsSync(proc.result) &&
                   scenario.scenario === 'restart-interrupted' && phase === 1) {
          const trace = loadJSON(join(lane, 'pre-interruption.json'))
          observed = { ...trace, code: 'interrupted', execution: 'indeterminate', pid: proc.pid }
        } else {
          observed = { pid: proc.pid, execution_error: { code: proc.code, signal: proc.signal,
            output_exists: existsSync(proc.result) } }
        }
        observed.process = { code: proc.code, signal: proc.signal, completionReceipt: existsSync(proc.result) }
      }
      const readback = observe(git, spec)
      observed = { ...observed, before, readback, ref: readback.ref, store: store.inspect() }
      phases.push(observed)
    }
    git('bundle', 'create', join(directory, 'fixture.bundle'), '--all')
    results.push({ id: scenario.id, phases })
  }
  saveJSON(join(rootOutput, 'run.json'), { mode, draw: packet.draw,
    inputs_sha256: sha(readFileSync(input)), cases: results })
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [mode, input, upstream, output] = process.argv.slice(2)
  assert(input && upstream && output, 'Usage: node study.mjs baseline|candidate <inputs> <pinned gate> <new output>')
  await run(mode, realpathSync(input), realpathSync(upstream), output)
}
