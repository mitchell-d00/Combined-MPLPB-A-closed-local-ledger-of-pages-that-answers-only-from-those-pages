import { execFileSync, spawn } from 'node:child_process'
import { closeSync, mkdirSync, openSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

export function gitRunner(repo, capture) {
  const env = {
    PATH: process.env.PATH, GIT_CONFIG_NOSYSTEM: '1', GIT_CONFIG_GLOBAL: '/dev/null',
    GIT_AUTHOR_DATE: '2026-11-27T00:00:00Z', GIT_COMMITTER_DATE: '2026-11-27T00:00:00Z',
  }
  return (...args) => {
    const fd = openSync(capture, 'w')
    try {
      execFileSync('git', ['-C', repo, ...args], { env, stdio: ['ignore', fd, 'inherit'] })
    } finally {
      closeSync(fd)
    }
    return readFileSync(capture, 'utf8').trim()
  }
}

export function fixture(directory, markers) {
  const repo = join(directory, 'repo')
  mkdirSync(repo)
  const git = gitRunner(repo, join(directory, 'driver-git.stdout'))
  git('init', '--quiet', '--template=', '--initial-branch=main')
  git('config', 'core.hooksPath', '/dev/null')
  git('config', 'user.name', 'MPLPB restart fixture')
  git('config', 'user.email', 'fixture@example.invalid')
  const commits = {}
  for (const marker of markers) {
    if (marker !== 'initial') git('switch', '--quiet', '--create', marker, commits.initial)
    writeFileSync(join(repo, 'marker'), marker + '\n')
    git('add', 'marker')
    git('commit', '--quiet', '-m', marker)
    commits[marker] = git('rev-parse', 'HEAD')
  }
  git('switch', '--quiet', 'main')
  git('branch', 'canary', commits.initial)
  return { repo, commits, ref: 'refs/heads/canary' }
}

export function observe(git, spec) {
  const oid = git('rev-parse', spec.ref)
  const marker = git('show', oid + ':marker')
  const ref = Object.keys(spec.commits).find(name => spec.commits[name] === oid)
  return { oid, ref: ref ?? 'unknown', marker }
}

export function child(entry, input, directory, name) {
  const config = join(directory, name + '.input.json')
  const result = join(directory, name + '.json')
  writeFileSync(config, JSON.stringify({ ...input, result }, null, 2) + '\n', { flag: 'wx' })
  const fd = openSync(join(directory, name + '.log'), 'wx')
  try {
    const proc = spawn(process.execPath, [entry, config], {
      env: { PATH: process.env.PATH }, stdio: ['ignore', fd, fd],
    })
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => proc.kill(), 15000)
      proc.once('error', error => { clearTimeout(timeout); reject(error) })
      proc.once('close', (code, signal) => {
        clearTimeout(timeout)
        resolve({ pid: proc.pid, code, signal, result })
      })
    })
  } finally {
    closeSync(fd)
  }
}

export function loadJSON(path) {
  return JSON.parse(readFileSync(path, 'utf8'))
}

export function saveJSON(path, value) {
  writeFileSync(path, JSON.stringify(value, null, 2) + '\n', { flag: 'wx' })
}

export function bindHost(template, { commits }, hostUsed) {
  const state = structuredClone(template)
  state.revision = commits.initial
  for (const collection of ['grants', 'reports', 'receipts']) {
    for (const entry of state[collection]) entry.revision = state.revision
  }
  if (hostUsed) state.used.push('record-canary:' + state.revision)
  return state
}
