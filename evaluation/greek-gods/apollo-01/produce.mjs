// Local synthetic producer. The Heka worker never receives signing keys.
import assert from 'node:assert/strict'
import { createHash,createPrivateKey,createPublicKey,sign } from 'node:crypto'
import { readFileSync,writeFileSync } from 'node:fs'

const { privateKeyPath,payload,result } = JSON.parse(readFileSync(process.argv[2],'utf8'))
const key = createPrivateKey(readFileSync(privateKeyPath))
assert.equal(key.asymmetricKeyType,'ed25519')
const publicKey = createPublicKey(key).export({type:'spki',format:'der'})
assert.equal(createHash('sha256').update(publicKey).digest('hex'),payload.producer)
const signature = sign(null,Buffer.from(JSON.stringify(payload)),key).toString('hex')
writeFileSync(result,JSON.stringify({payload,signature},null,2)+'\n',{flag:'wx'})
