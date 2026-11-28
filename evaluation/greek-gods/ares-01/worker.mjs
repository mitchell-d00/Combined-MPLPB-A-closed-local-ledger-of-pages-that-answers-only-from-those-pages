/** Restricted instrumentation of the pinned Heka lab worker. */
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { registerHooks } from 'node:module'
import { loadJSON,saveJSON } from '../../comparative-tests/workflow-controller/restart/fixture.mjs'
import { current,event } from './authority.mjs'

const input = loadJSON(process.argv[2])
if (input.mode==='prime') {
  const grant = current(input.authorityRoot)
  event(input.authorityRoot,'prime:'+grant.epoch)
  saveJSON(input.result,{pid:process.pid,grant})
} else {
  const bridge = new URL('../../egyptian-gods/heka-01/bridge.mjs',import.meta.url)
  const lock = loadJSON(new URL('./freeze.json',import.meta.url))
  const source = readFileSync(bridge,'utf8')
  assert.equal(createHash('sha256').update(source).digest('hex'),
    lock.preserved['evaluation/egyptian-gods/heka-01/bridge.mjs'])
  let instrumented = 'import { createControl } from '+JSON.stringify(new URL('./authority.mjs',import.meta.url).href)+';\n'+source
  const changes = [
    ['async function main(input) {','async function main(input) {\n  const control = createControl(input)'],
    ["return { ...state, revision: git('rev-parse', 'HEAD'), receipts:",
     "return { ...state, grants: control.grants(state.grants), revision: git('rev-parse', 'HEAD'), receipts:"],
    ['    beforeWrite() {','    beforeWrite() {\n      control.beforeFinal()'],
    ['    writeCanary(scope) {','    writeCanary(scope) {\n      control.admitted()'],
    ['      trace.attempts++','      trace.attempts++\n      control.effect()'],
    ["        durableVerdict = 'completed'","        durableVerdict = 'completed'\n        control.completed()"],
  ]
  for (const [original,replacement] of changes) {
    assert.equal(instrumented.split(original).length,2)
    instrumented=instrumented.replace(original,replacement)
  }
  const hook=registerHooks({
    load(url,context,nextLoad) {
      const loaded=nextLoad(url,context)
      if (url!==bridge.href) return loaded
      assert.equal(loaded.source.toString(),source)
      return { ...loaded,source:instrumented }
    },
  })
  try { await import(bridge.href) }
  finally { hook.deregister() }
}
