/**
 * Lab-only receipt operand injection. Pin the historical module and replace
 * exactly one initializer in memory. All proof, policy and effect code runs
 * from that module. An ordinary local control never substitutes an operand.
 */
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { registerHooks } from 'node:module'

const bridge = new URL('../../egyptian-gods/heka-01/bridge.mjs', import.meta.url)
const freeze = JSON.parse(readFileSync(new URL('./freeze.json', import.meta.url), 'utf8'))
const source = readFileSync(bridge, 'utf8')
assert.equal(createHash('sha256').update(source).digest('hex'), freeze.bridge_sha256)
const needle = "  const binding = scenario === 'wrong-receipt'"
assert.equal(source.split(needle).length, 2)
const replacement = "  const binding = Object.hasOwn(input, 'labBinding') ? input.labBinding : scenario === 'wrong-receipt'"
const hook = registerHooks({
  load(url, context, nextLoad) {
    const result = nextLoad(url, context)
    if (url !== bridge.href) return result
    assert.equal(result.source.toString(), source)
    return { ...result, source: source.replace(needle, replacement) }
  },
})
try {
  await import(bridge.href)
} finally {
  hook.deregister()
}
