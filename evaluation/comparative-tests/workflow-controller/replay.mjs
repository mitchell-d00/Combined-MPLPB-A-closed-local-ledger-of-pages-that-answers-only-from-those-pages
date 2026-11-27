import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { closeSync, mkdtempSync, openSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { controllerFactory } from './controller.mjs'

const [gatePath, suite, output] = process.argv.slice(2)
assert(gatePath && output && ['shadow', 'development', 'canary', 'held', 'competing-writer'].includes(suite),
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

function withCanaryRepository(run, markers = { initial: 'before', intended: 'after' }) {
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
    const initial = commitMarker(markers.initial)
    git('branch', 'canary', initial)
    git('switch', '--quiet', '--create', 'payload')
    const payload = commitMarker(markers.intended)
    git('switch', '--quiet', 'main')
    let competing
    if (markers.competing) {
      git('switch', '--quiet', '--create', 'competing')
      competing = commitMarker(markers.competing)
      git('switch', '--quiet', 'main')
    }
    const ref = 'refs/heads/canary'
    const snapshot = () => {
      const observed = git('rev-parse', ref)
      return { ref: observed, marker: git('show', observed + ':marker') }
    }
    return run({ git, initial, payload, competing, ref, snapshot })
  } finally {
    rmSync(repo, { recursive: true, force: true })
  }
}

function bindRevision(template, initial) {
  const state = structuredClone(template)
  for (const kind of ['grants', 'receipts', 'reports']) {
    for (const entry of state[kind]) entry.revision = initial
  }
  return state
}

function canary({ template, cases }) {
  return withCanaryRepository(({ git, initial, payload, ref, snapshot }) => {
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
      state = bindRevision(template, initial)
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
  })
}

function competingWriter({ setup, cases }, template) {
  return cases.map(({ id, competing_write: hasCompetitor, expect }) =>
    withCanaryRepository(({ git, initial, payload, competing, ref, snapshot }) => {
      assert.equal(ref, setup.ref)
      const state = bindRevision(template, initial)
      const proposal = { action: 'record-canary', revision: initial }
      const commits = { initial, intended: payload, competing }
      let afterHook, casExit
      let hookCalls = 0
      let controllerAttempts = 0
      const board = create({
        readState: () => ({ ...state, revision: git('rev-parse', 'HEAD') }),
        beforeWrite() {
          hookCalls++
          if (hasCompetitor) git('update-ref', ref, competing, initial)
          afterHook = snapshot()
        },
        writeCanary(scope) {
          controllerAttempts++
          try {
            git('update-ref', ref, payload, scope.revision)
            casExit = 0
          } catch (error) {
            casExit = error.status
            throw error
          }
        },
      })
      const before = snapshot()
      const initialAdmission = board.evaluate(proposal)
      const attempt = board.run(proposal)
      const afterAttempt = snapshot()
      const duplicate = board.run(proposal)
      const afterDuplicate = snapshot()
      const controllerUpdates = Number(Boolean(afterHook && afterHook.ref !== afterAttempt.ref &&
        afterAttempt.ref === payload))
      const competingUpdates = Number(Boolean(afterHook && before.ref !== afterHook.ref &&
        afterHook.ref === competing))
      const matches = (actual, name) => actual?.ref === commits[name] && actual.marker === setup.markers[name]
      const passed = matches(before, 'initial') && matches(afterHook, expect.after_hook) &&
        matches(afterAttempt, expect.after_attempt) && matches(afterDuplicate, expect.after_duplicate) &&
        initialAdmission.decision === expect.admission && attempt.verdict.decision === expect.admission &&
        attempt.execution === expect.execution && duplicate.execution === expect.duplicate.execution &&
        duplicate.verdict.code === expect.duplicate.code && hookCalls === expect.hook_calls &&
        controllerAttempts === expect.controller_attempts && controllerUpdates === expect.controller_updates &&
        competingUpdates === expect.competing_updates &&
        (expect.execution === 'completed' ? casExit === 0 : Number.isInteger(casExit) && casExit > 0)
      return { id, expect, commits, before, initialAdmission, afterHook, attempt, casExit, afterAttempt,
        duplicate, afterDuplicate, hookCalls, controllerAttempts, controllerUpdates, competingUpdates, passed }
    }, setup.markers))
}

if (suite === 'competing-writer') {
  const { template } = JSON.parse(readFileSync(new URL('canary.json', import.meta.url), 'utf8'))
  const rows = competingWriter(packet, template)
  const summary = {
    cases: rows.length,
    matches: rows.filter(row => row.passed).length,
    admissions: rows.filter(row => row.attempt.verdict.decision === 'allow').length,
    completed: rows.filter(row => row.attempt.execution === 'completed').length,
    failed: rows.filter(row => row.attempt.execution === 'failed').length,
    controllerUpdates: rows.reduce((count, row) => count + row.controllerUpdates, 0),
    competingUpdates: rows.reduce((count, row) => count + row.competingUpdates, 0),
  }
  writeFileSync(output, JSON.stringify({ suite, summary, rows }, null, 2) + '\n', { flag: 'wx' })
  console.log(suite, summary)
  process.exit(summary.matches === summary.cases ? 0 : 1)
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
