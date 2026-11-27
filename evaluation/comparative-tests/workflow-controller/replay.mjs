import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { closeSync, mkdtempSync, openSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { controllerFactory } from './controller.mjs'

const [gatePath, suite, output] = process.argv.slice(2)
assert(gatePath && output && ['shadow', 'development', 'canary', 'held'].includes(suite),
  'Usage: node replay.mjs <pinned B-Tests index.mjs> <suite> <new-output.json>')
const create = await controllerFactory(gatePath)
const packet = JSON.parse(readFileSync(new URL(suite + '.json', import.meta.url), 'utf8'))

function shadow(cases) {
  return cases.map(({ id, state, proposal, expect, observed, record, source }) => {
    const gate = create({ readState: () => state })
    const verdict = gate.evaluate(proposal)
    return {
      id, expect, verdict, ...(observed ? { observed, record, source, disagreement: observed !== verdict.decision } : {}),
      passed: verdict.decision === expect.decision && verdict.code === expect.code &&
        (verdict.decision !== 'allow' || (verdict.scope?.revision === proposal.revision &&
          verdict.scope.action === proposal.action && verdict.selected.grant !== null &&
          verdict.selected.report !== null && verdict.receiptIds.length > 0)),
    }
  })
}

function canary({ template, cases }) {
  const repo = mkdtempSync(join(tmpdir(), 'mplpb-workflow-canary-'))
  // No inherited Git-dir/index/worktree selection and no network remotes.
  const env = Object.fromEntries(Object.entries(process.env).filter(([key]) => !key.startsWith('GIT_')))
  env.GIT_CONFIG_NOSYSTEM = '1'
  env.GIT_CONFIG_GLOBAL = '/dev/null'
  const capture = join(repo, '.git-output')
  function git(...args) {
    // Use a file descriptor so the local harness needs no IPC socket.
    const fd = openSync(capture, 'w')
    try {
      execFileSync('git', ['-C', repo, ...args], { env, stdio: ['ignore', fd, 'inherit'] })
    } finally {
      closeSync(fd)
    }
    return readFileSync(capture, 'utf8').trim()
  }
  try {
    git('init', '--quiet', '--template=', '--initial-branch=main')
    git('config', 'user.name', 'Disposable MPLPB canary')
    git('config', 'user.email', 'canary@example.invalid')
    git('config', 'core.hooksPath', '/dev/null')
    function commitMarker(marker) {
      writeFileSync(join(repo, 'marker'), marker + '\n')
      git('add', 'marker')
      git('commit', '--quiet', '-m', marker)
      return git('rev-parse', 'HEAD')
    }
    const initial = commitMarker('before')
    git('branch', 'canary', initial)
    git('switch', '--quiet', '--create', 'payload')
    const payload = commitMarker('after')
    git('switch', '--quiet', 'main')
    const ref = 'refs/heads/canary'
    const snapshot = () => ({ ref: git('rev-parse', ref), marker: git('show', ref + ':marker') })
    let state, revoke
    const gate = create({
      readState: () => ({ ...state, revision: git('rev-parse', 'HEAD') }),
      beforeWrite: () => { if (revoke) state.grants[0].status = 'revoked' },
      writeCanary: scope => {
        assert.equal(scope.revision, initial)
        git('update-ref', ref, payload, initial)
      },
    })
    return cases.map(({ id, scenario, expect, effect }) => {
      state = structuredClone(template)
      for (const kind of ['grants', 'receipts', 'reports']) {
        for (const entry of state[kind]) entry.revision = initial
      }
      const proposal = { action: 'record-canary', revision: initial }
      revoke = scenario === 'revoke-before-write'
      if (scenario === 'blocked-role') state.session.role = 'Al'
      if (scenario === 'wrong-revision') proposal.revision = payload
      if (scenario === 'stale-receipt') state.receipts[0].revision = payload
      if (scenario === 'conflicting-receipts') {
        state.receipts.push({ ...state.receipts[0], id: 'conflicting', semantic: 'failed' })
      }
      if (scenario === 'revoked-grant') state.grants[0].status = 'revoked'
      const before = snapshot()
      const { verdict, execution } = gate.run(proposal)
      const after = snapshot()
      const wrote = before.ref !== after.ref
      const contentsMatch = effect ? after.ref === payload && after.marker === 'after' :
        before.ref === after.ref && before.marker === after.marker
      return { id, scenario, expect, effect, verdict, execution,
        before: before.marker, after: after.marker, refChanged: wrote,
        passed: verdict.code === expect && wrote === effect && contentsMatch &&
          execution === (effect ? 'completed' : 'not_run') }
    })
  } finally {
    rmSync(repo, { recursive: true, force: true })
  }
}

const rows = suite === 'canary' ? canary(packet) : shadow(packet)
const summary = {
  cases: rows.length,
  matches: rows.filter(row => row.passed).length,
  correctAdmissions: rows.filter(row => row.passed && row.verdict.decision === 'allow').length,
  falseAdmissions: rows.filter(row => row.verdict.decision === 'allow' &&
    (typeof row.effect === 'boolean' ? !row.effect : row.expect.decision !== 'allow')).length,
  falseDenials: rows.filter(row => row.verdict.decision !== 'allow' &&
    (typeof row.effect === 'boolean' ? row.effect : row.expect.decision === 'allow')).length,
  protectedOutcomes: rows.filter(row => row.passed && row.verdict.decision !== 'allow').length,
  executionFailures: rows.filter(row => row.execution === 'failed').length,
  realWrites: rows.filter(row => row.refChanged).length,
  historicalLabelDifferences: rows.filter(row => row.disagreement).map(row => row.id),
}
writeFileSync(output, JSON.stringify({ suite, summary, rows }, null, 2) + '\n', { flag: 'wx' })
console.log(suite, summary)
if (summary.matches !== summary.cases) process.exitCode = 1
