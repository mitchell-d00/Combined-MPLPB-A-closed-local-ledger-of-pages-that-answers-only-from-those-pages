import { createHash,createPublicKey,verify } from 'node:crypto'

export function checkReceipt({payload,signature},trust) {
  const producer = Object.values(trust.entries).find(entry => entry.fingerprint === payload?.producer)
  const outcome = { producer:producer?.status ?? 'unaccepted',signature_valid:false }
  if (!producer || payload.schema !== 'apollo01-signed-receipt-v1' ||
      !/^[0-9a-f]{128}$/.test(signature)) return outcome
  const key = createPublicKey(producer.verificationKey)
  const bytes = key.export({type:'spki',format:'der'})
  if (key.asymmetricKeyType !== 'ed25519' ||
      createHash('sha256').update(bytes).digest('hex') !== producer.fingerprint) return outcome
  outcome.signature_valid = verify(null,Buffer.from(JSON.stringify(payload)),key,Buffer.from(signature,'hex'))
  return outcome
}
