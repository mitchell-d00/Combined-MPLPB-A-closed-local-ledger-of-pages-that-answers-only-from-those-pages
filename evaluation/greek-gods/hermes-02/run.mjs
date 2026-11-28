import assert from 'node:assert/strict'
import { lstatSync, mkdirSync, readFileSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { reader, sha } from '../../egyptian-gods/heka-01/study.mjs'
import { child, fixture, gitRunner, loadJSON, observe, saveJSON } from '../../comparative-tests/workflow-controller/restart/fixture.mjs'
import { reservations } from '../../comparative-tests/workflow-controller/restart/reservation.mjs'

const hash = value => sha(JSON.stringify(value))
const freeze = loadJSON(new URL('./freeze.json', import.meta.url))
const worker = fileURLToPath(new URL('./seam.mjs', import.meta.url))
const [inputs, gate, outputPath] = process.argv.slice(2)
assert(inputs && gate && outputPath, 'Usage: node run.mjs <sealed packet> <pinned gate> <new output>')
const packet = loadJSON(inputs)
const upstream = resolve(gate)
const output = resolve(outputPath)
assert.equal(packet.schema, 'hermes02-packet-v1')
const inputs_sha256 = sha(readFileSync(inputs))
assert.equal(inputs_sha256, freeze.draws[packet.draw].inputs)
assert.equal(packet.phases.length, freeze.draws[packet.draw].phases)
assert.equal(sha(readFileSync(upstream)), freeze.upstream_gate_sha256)
for (const [name,digest] of Object.entries(freeze.apparatus)) {
  assert.equal(sha(readFileSync(new URL(name, import.meta.url))), digest)
}
mkdirSync(output)
const ledger = join(output, 'ledger')
const prepare = join(output, 'case.json')
saveJSON(prepare, { ...packet, scenario: 'positive' })
reader('prepare', ledger, prepare)
const targets = {}, git = {}, stores = {}
for (const host of ['A','B']) {
  const root = join(output,host)
  mkdirSync(root)
  const spec = fixture(root,['initial','intended','competing'])
  const namespace = join(root,'store')
  mkdirSync(namespace)
  targets[host] = { ...spec, namespace }
  git[host] = gitRunner(spec.repo, join(root,'driver-git.stdout'))
  stores[host] = reservations(namespace,'record-canary:'+spec.commits.initial)
}
assert.deepEqual(targets.A.commits, targets.B.commits)

function storeFiles(root) {
  const entries = []
  function visit(dir, prefix) {
    for (const name of readdirSync(dir).sort()) {
      const path = join(dir,name)
      const relative = prefix+name
      const stat = lstatSync(path)
      if (stat.isDirectory()) {
        entries.push([relative,null])
        visit(path,relative+'/')
      } else {
        assert(stat.isFile())
        entries.push([relative,sha(readFileSync(path))])
      }
    }
  }
  visit(root,'')
  return entries
}

function readTargets() {
  return Object.fromEntries(['A','B'].map(host => [host,{
    ref:observe(git[host],targets[host]),store:stores[host].inspect(),
    storeFiles:storeFiles(targets[host].namespace),
  }]))
}

const initial = readTargets()
const own = new Map(), traces=[]
for (const phase of packet.phases) {
  assert.match(phase.id,/^HERMES02-[DF]-\d\d$/)
  assert(['A','B'].includes(phase.target))
  const spec = targets[phase.target]
  const lane = join(output,phase.id)
  mkdirSync(lane)
  const caseFile = join(lane,'input-case.json')
  saveJSON(caseFile, { question:packet.question,obligation:packet.obligation,
    scenario:phase.authority==='revoke' ? 'revoked' : 'positive' })
  const config = { spec, lane, ledger, caseFile, upstream, storePath:spec.namespace,
    phase:1, authority:phase.authority==='absent' ? 'absent' : 'grant', readerPin:freeze.baseline }
  if (phase.binding === 'repeat') {
    assert(own.has(phase.target))
    config.labBinding = own.get(phase.target)
  } else if (phase.binding === 'foreign' || phase.binding === 'mutated') {
    const donated = own.get(packet.donor)
    assert(donated)
    config.labBinding = phase.binding === 'foreign' ? donated : { ...donated,
      target:{ ...donated.target,namespace:donated.target.namespace+'-contrast' } }
  } else {
    assert.equal(phase.binding,'local')
  }
  const before = readTargets()
  const proc = await child(worker,config,lane,'worker')
  assert.equal(proc.code,0,'Worker failed at '+phase.id)
  assert.equal(proc.signal,null)
  const trace = loadJSON(proc.result)
  if (trace.execution === 'completed') own.set(phase.target,trace.binding)
  traces.push({ id:phase.id, before, after:readTargets(),child_pid:proc.pid,
    binding_sha256:hash(trace.binding),trace })
}
for (const [host,target] of Object.entries(targets)) {
  const path=join(output,host,'fixture.bundle')
  git[host]('bundle','create',path,'--all')
  git[host]('bundle','verify',path)
  assert.equal(target.ref,'refs/heads/canary')
}
saveJSON(join(output,'run.json'),{ draw:packet.draw,inputs_sha256,bridge_sha256:freeze.bridge_sha256,
  targets,initial,phases:traces })
