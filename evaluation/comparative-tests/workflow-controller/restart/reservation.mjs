import { createHash } from 'node:crypto'
import { closeSync, fsyncSync, lstatSync, mkdirSync, openSync, readFileSync,
  renameSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

function syncDirectory(path) {
  const fd = openSync(path, 'r')
  try { fsyncSync(fd) } finally { closeSync(fd) }
}

export function reservations(root, key) {
  const path = join(root, createHash('sha256').update(key).digest('hex'))
  const requireStore = () => {
    if (!lstatSync(root).isDirectory()) throw new Error('Reservation store needs an existing directory')
  }
  return {
    inspect() {
      try { requireStore() } catch { return 'unavailable' }
      try {
        if (!lstatSync(path).isDirectory()) return 'pending'
      } catch (error) {
        return error.code === 'ENOENT' ? 'unused' : 'unavailable'
      }
      try {
        const receipt = JSON.parse(readFileSync(join(path, 'outcome.json'), 'utf8'))
        if (receipt.key === key && /^[a-f0-9]{40}$/.test(receipt.ref?.oid)) {
          if (receipt.status === 'completed' && receipt.ref.marker === 'intended') return 'completed'
          if (receipt.status === 'failed' && receipt.ref.marker === 'competing') return 'failed'
        }
      } catch {
        // A missing, unreadable or invalid receipt leaves the claim consumed.
      }
      return 'pending'
    },
    claim() {
      requireStore()
      try {
        mkdirSync(path, { mode: 0o700 })
      } catch (error) {
        if (error.code === 'EEXIST') return false
        throw error
      }
      syncDirectory(root)
      return true
    },
    finish(status, ref) {
      const staging = join(path, 'outcome.tmp')
      const fd = openSync(staging, 'wx', 0o600)
      try {
        writeFileSync(fd, JSON.stringify({ key, status, ref }) + '\n')
        fsyncSync(fd)
      } finally {
        closeSync(fd)
      }
      renameSync(staging, join(path, 'outcome.json'))
      syncDirectory(path)
    },
  }
}
