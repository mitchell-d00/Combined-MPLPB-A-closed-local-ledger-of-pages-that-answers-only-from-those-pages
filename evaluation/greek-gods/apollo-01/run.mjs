import assert from 'node:assert/strict'
import { mkdirSync,readFileSync,readdirSync,unlinkSync } from 'node:fs'
import { join,resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { nativeStatus,reader,sha } from '../../egyptian-gods/heka-01/study.mjs'
import { child,fixture,gitRunner,loadJSON,observe,saveJSON } from '../../comparative-tests/workflow-controller/restart/fixture.mjs'
import { reservations } from '../../comparative-tests/workflow-controller/restart/reservation.mjs'
import { checkReceipt } from './check.mjs'

const local = name => new URL(name,import.meta.url)
const path = name => fileURLToPath(local(name))
const hash = value => sha(JSON.stringify(value))
const freeze = loadJSON(local('./freeze.json'))
const trust = loadJSON(local('./trust.json'))
const [inputs,gate,keys,outputPath] = process.argv.slice(2)
assert(inputs && gate && keys && outputPath,'Usage: node run.mjs <sealed operator packet> <pinned gate> <lab producer key directory> <new output>')
const upstream = resolve(gate)
const output = resolve(outputPath)
const packet = loadJSON(inputs)
assert.equal(packet.schema,'apollo01-packet-v1')
assert.equal(packet.cases.length,freeze.draws[packet.draw].cases)
const inputs_sha256 = sha(readFileSync(inputs))
const trust_sha256 = sha(readFileSync(local('./trust.json')))
assert.equal(inputs_sha256,freeze.draws[packet.draw].inputs)
assert.equal(trust_sha256,freeze.trust_sha256)
assert.equal(sha(readFileSync(upstream)),freeze.upstream_gate_sha256)
for (const [name,digest] of Object.entries(freeze.apparatus))
  assert.equal(sha(readFileSync(local(name))),digest)
for (const [name,digest] of Object.entries(freeze.preserved))
  assert.equal(sha(readFileSync(local('../../../'+name))),digest)

mkdirSync(output)
const rows = []
for (const c of packet.cases) {
  assert.match(c.id,/^APOLLO-[DF]-\d\d$/)
  const dir = join(output,c.id)
  mkdirSync(dir)
  const spec = fixture(dir,['initial','intended','competing'])
  const git = gitRunner(spec.repo,join(dir,'driver-git.stdout'))
  const ledger = join(dir,'ledger')
  const storePath = join(dir,'store')
  mkdirSync(storePath)
  const store = reservations(storePath,'record-canary:'+spec.commits.initial)
  const readback = () => ({ ref:observe(git,spec),store:store.inspect(),
    reservation_files:readdirSync(storePath,{recursive:true}).sort() })
  const caseFile = join(dir,'case.json')
  saveJSON(caseFile,c)
  reader('prepare',ledger,caseFile)
  const raw = reader('probe',ledger,caseFile)
  saveJSON(join(dir,'producer-proof.json'),raw)
  const proof = nativeStatus(raw)
  const authority = c.scenario === 'missing-grant' ? 'absent' : 'grant'
  const target = { action:'record-canary',ref:spec.ref,revision:spec.commits.initial,
    intended:spec.commits.intended,namespace:storePath }
  const signedTarget = { ...target }
  if (c.scenario === 'wrong-namespace') signedTarget.namespace += '-alternate'
  if (c.scenario === 'wrong-target') signedTarget.revision = spec.commits.competing
  const binding = { schema:'heka-proof-binding-v1',readerPin:freeze.baseline,
    question:c.question,obligation:c.obligation,snapshot:hash(raw.snapshot),
    proof:hash(raw.answer),target:signedTarget }
  const kind = { 'unknown-key':'unaccepted','retired-key':'retired' }[c.scenario] ?? 'active'
  const payload = { schema:'apollo01-signed-receipt-v1',producer:trust.entries[kind].fingerprint,binding }
  const signer = await child(path('./produce.mjs'),{
    privateKeyPath:resolve(keys,kind+'.pem'),payload,
  },dir,'producer')
  assert.equal(signer.code,0)
  assert.equal(signer.signal,null)
  unlinkSync(join(dir,'producer.input.json'))
  const envelope = loadJSON(signer.result)
  if (c.scenario === 'changed-payload') envelope.payload.binding.proof = '0'.repeat(64)
  saveJSON(join(dir,'submitted.json'),envelope)
  const before = readback()
  const outcome = { ...checkReceipt(envelope,trust),proof,authority,binding:'unreached',
    initial_admission:null,final_admission:null,code:null,attempts:0,writes:0,execution:'not_run' }
  let trace = null
  if (!outcome.signature_valid) {
    outcome.code = 'signature_invalid'
  } else if (outcome.producer !== 'active') {
    outcome.code = 'producer_not_active'
  } else {
    const proc = await child(path('../hermes-02/seam.mjs'),{ spec,upstream,lane:dir,ledger,caseFile,storePath,
      phase:1,authority,readerPin:freeze.baseline,labBinding:envelope.payload.binding },dir,'bridge')
    assert.equal(proc.code,0)
    assert.equal(proc.signal,null)
    trace = loadJSON(proc.result)
    assert.equal(trace.pid,proc.pid)
    assert.equal(trace.proof,proof)
    outcome.code = trace.code
    outcome.binding = trace.code === 'receipt_binding_mismatch' ? 'mismatch'
      : trace.binding === null ? 'unreached' : 'matched'
    outcome.initial_admission = trace.admission?.decision ?? null
    outcome.final_admission = trace.controller?.verdict?.decision ?? null
    for (const key of ['attempts','writes','execution']) outcome[key] = trace[key]
  }
  const after = readback()
  outcome.marker = after.ref.marker
  outcome.store = after.store
  const bundle = join(dir,'fixture.bundle')
  git('bundle','create',bundle,'--all')
  git('bundle','verify',bundle)
  rows.push({id:c.id,commits:spec.commits,producer_pid:signer.pid,
    payload_sha256:hash(envelope.payload),outcome,before,after,trace})
}
saveJSON(join(output,'run.json'),{draw:packet.draw,inputs_sha256,trust_sha256,cases:rows})
