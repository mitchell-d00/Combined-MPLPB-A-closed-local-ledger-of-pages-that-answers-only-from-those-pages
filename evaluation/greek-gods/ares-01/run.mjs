import assert from 'node:assert/strict'
import { mkdirSync,readFileSync,readdirSync } from 'node:fs'
import { join,resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { reader,sha } from '../../egyptian-gods/heka-01/study.mjs'
import { child,fixture,gitRunner,loadJSON,observe,saveJSON } from '../../comparative-tests/workflow-controller/restart/fixture.mjs'
import { reservations } from '../../comparative-tests/workflow-controller/restart/reservation.mjs'
import { current,signal } from './authority.mjs'

const url = name => new URL(name,import.meta.url)
const path = name => fileURLToPath(url(name))
const lock = loadJSON(url('./freeze.json'))
const [inputs,gate,targetPath] = process.argv.slice(2)
assert(inputs && gate && targetPath,'Usage: node run.mjs <sealed input> <pinned gate> <new output>')
const packet=loadJSON(inputs)
assert.equal(packet.schema,'ares01-packet-v1')
assert.equal(packet.cases.length,lock.draws[packet.draw].cases)
const inputs_sha256=sha(readFileSync(inputs))
assert.equal(inputs_sha256,lock.draws[packet.draw].inputs)
const upstream=resolve(gate)
assert.equal(sha(readFileSync(upstream)),lock.upstream_gate_sha256)
for (const [name,digest] of Object.entries(lock.apparatus))
  assert.equal(sha(readFileSync(url(name))),digest)
for (const [name,digest] of Object.entries(lock.preserved))
  assert.equal(sha(readFileSync(url('../../../'+name))),digest)

const output=resolve(targetPath)
mkdirSync(output)
const rows=[]
function resultOf(proc) {
  assert.equal(proc.code,0)
  assert.equal(proc.signal,null)
  const data=loadJSON(proc.result)
  assert.equal(data.pid,proc.pid)
  return data
}
for(const c of packet.cases) {
  assert.match(c.id,/^ARES-[DF]-\d\d$/)
  const dir=join(output,c.id)
  mkdirSync(dir)
  const spec=fixture(dir,['initial','intended','competing'])
  const git=gitRunner(spec.repo,join(dir,'driver-git.stdout'))
  const ledger=join(dir,'ledger'), storePath=join(dir,'store')
  mkdirSync(storePath)
  const store=reservations(storePath,'record-canary:'+spec.commits.initial)
  const readback=()=>({ref:observe(git,spec),store:store.inspect(),
    reservation_files:readdirSync(storePath,{recursive:true}).sort()})
  const caseFile=join(dir,'case.json')
  saveJSON(caseFile,c)
  reader('prepare',ledger,caseFile)
  saveJSON(join(dir,'authority.json'),{epoch:1,status:'active'})
  const before=readback()
  const state={spec,upstream,lane:dir,ledger,caseFile,storePath,phase:1,
    authority:'grant',readerPin:lock.baseline,authorityRoot:dir,experiment:c.scenario}
  const pids={driver:process.pid}
  const point={'pre-check':'pre','stale-cache':'cache','post-check':'post',restart:'restart'}[c.scenario]
  let revoker
  if (point) revoker=child(path('./revoke.mjs'),{root:dir,point},dir,'revoker')
  if (point==='restart') {
    const primed=resultOf(await child(path('./worker.mjs'),{mode:'prime',authorityRoot:dir},dir,'prime'))
    assert.equal(primed.grant.epoch,1)
    pids.prime=primed.pid
    signal(dir,point)
    pids.revoker=resultOf(await revoker).pid
  }
  const trace=resultOf(await child(path('./worker.mjs'),state,dir,'worker'))
  pids.worker=trace.pid
  if(revoker && point!=='restart') pids.revoker=resultOf(await revoker).pid
  const after=readback()
  const outcome={code:trace.code,proof:trace.proof,initial:trace.admission?.decision??null,
    final:trace.controller?.verdict?.decision??null,attempts:trace.attempts,writes:trace.writes,
    execution:trace.execution,marker:after.ref.marker,store:after.store,authority_epoch:current(dir).epoch}
  const bundle=join(dir,'fixture.bundle')
  git('bundle','create',bundle,'--all')
  git('bundle','verify',bundle)
  rows.push({id:c.id,pids,commits:spec.commits,before,after,outcome,trace})
}
saveJSON(join(output,'run.json'),{draw:packet.draw,inputs_sha256,cases:rows})
