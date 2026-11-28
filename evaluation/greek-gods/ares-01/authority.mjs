import assert from 'node:assert/strict'
import { appendFileSync,existsSync,readFileSync,renameSync,writeFileSync } from 'node:fs'
import { join } from 'node:path'

export function event(root,name) {
  appendFileSync(join(root,'events.jsonl'),JSON.stringify({ event:name,pid:process.pid })+'\n')
}

export function current(root) {
  const grant = JSON.parse(readFileSync(join(root,'authority.json'),'utf8'))
  assert((grant.epoch===1 && grant.status==='active') || (grant.epoch===2 && grant.status==='revoked'))
  return grant
}

export function publish(path,value) {
  writeFileSync(path+'.new',value,{flag:'wx'})
  renameSync(path+'.new',path)
}

export function signal(root,point) {
  event(root,'signal:'+point)
  publish(join(root,'signal'),point+'\n')
}

export function waitFor(path) {
  const wait = new Int32Array(new SharedArrayBuffer(4))
  const deadline = performance.now()+9000
  while (!existsSync(path)) {
    if (performance.now()>deadline) throw new Error('Timed out awaiting '+path)
    Atomics.wait(wait,0,0,5)
  }
}

export function createControl({authorityRoot:root,experiment}) {
  let cache
  if (experiment==='stale-cache') {
    cache = current(root)
    assert.equal(cache.epoch,1)
    event(root,'cache:'+cache.epoch)
    handshake('cache')
  }
  let reads = 0
  function handshake(point) {
    signal(root,point)
    const ack = join(root,'ack')
    waitFor(ack)
    assert.equal(readFileSync(ack,'utf8'),point+'\n')
  }
  return {
    grants(owners) {
      assert(++reads<=3)
      const cached = cache && reads<3
      const grant = cached ? cache : current(root)
      event(root,'read:'+reads+':'+(cached?'cached':'shared')+':'+grant.epoch)
      const status = grant.status==='active' ? 'active' : 'revoked'
      return owners.map(owner=>({...owner,status}))
    },
    beforeFinal() {
      assert.equal(reads,2)
      if (experiment==='pre-check') handshake('pre')
    },
    admitted() {
      assert.equal(reads,3)
      event(root,'scope-admitted')
      if (experiment==='post-check') handshake('post')
    },
    effect() { event(root,'writer-attempt') },
    completed() { event(root,'durable-completed') },
  }
}
