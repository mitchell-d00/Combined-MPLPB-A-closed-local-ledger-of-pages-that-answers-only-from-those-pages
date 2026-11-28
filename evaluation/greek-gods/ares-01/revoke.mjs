/** A separate local revoker waits for a named barrier and commits epoch 2. */
import assert from 'node:assert/strict'
import { readFileSync,renameSync } from 'node:fs'
import { join } from 'node:path'
import { loadJSON,saveJSON } from '../../comparative-tests/workflow-controller/restart/fixture.mjs'
import { current,event,publish,waitFor } from './authority.mjs'

const { root,point,result } = loadJSON(process.argv[2])
const signal = join(root,'signal')
waitFor(signal)
assert.equal(readFileSync(signal,'utf8'),point+'\n')
assert.deepEqual(current(root),{epoch:1,status:'active'})
const staged=join(root,'authority.new')
saveJSON(staged,{epoch:2,status:'revoked'})
renameSync(staged,join(root,'authority.json'))
event(root,'revoked:2')
publish(join(root,'ack'),point+'\n')
saveJSON(result,{pid:process.pid,point,grant:current(root)})
