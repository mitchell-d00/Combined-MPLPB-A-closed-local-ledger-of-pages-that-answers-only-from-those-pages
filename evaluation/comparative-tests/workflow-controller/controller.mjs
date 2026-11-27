import { readFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'

const upstreamHash = '5e71d0b7fc3f64294b726e8108a08d9ff0e79552a8975ee379aaa2546e988291'
const rules = new Map([
  ['run-tests', ['prepared', ['input-freeze']]],
  ['merge', ['tested', ['candidate-tests', 'release-acceptance']]],
  ['deploy', ['merged', ['merge-event', 'deployment-package']]],
  ['record-canary', ['prepared', ['canary-ready']]],
])
const token = value => typeof value === 'string' && /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(value)
const revision = value => typeof value === 'string' && /^[a-f0-9]{40}$/.test(value)
const record = value => value !== null && typeof value === 'object' &&
  [Object.prototype, null].includes(Object.getPrototypeOf(value))
const list = (items, check) => Array.isArray(items) && Array.from(items).every(check)
const records = (items, check) => list(items, item => record(item) && token(item.id) && check(item)) &&
  new Set(items.map(item => item.id)).size === items.length
const oneOf = (value, ...allowed) => allowed.includes(value)
const requiredBy = (action, kind) => rules.get(action)?.[1].includes(kind)

function validState(state) {
  return record(state) && revision(state.revision) &&
    record(state.session) && token(state.session.id) && token(state.session.role) &&
    list(state.session.capabilities, action => rules.has(action)) &&
    records(state.grants, g => token(g.issuer) && token(g.session) && rules.has(g.action) &&
      revision(g.revision) && oneOf(g.status, 'active', 'revoked')) &&
    records(state.reports, r => oneOf(r.kind, 'applied', 'advice') && revision(r.revision)) &&
    records(state.receipts, r => rules.has(r.action) && token(r.kind) && revision(r.revision) &&
      oneOf(r.availability, 'available', 'unavailable') &&
      oneOf(r.execution, 'completed', 'failed', 'not_run') &&
      oneOf(r.semantic, 'passed', 'failed', 'not_run')) &&
    oneOf(state.custody, 'public', 'restricted', 'unavailable') &&
    oneOf(state.release, 'prepared', 'tested', 'merged', 'deployed') &&
    list(state.used, value => typeof value === 'string' && /^(run-tests|merge|deploy|record-canary):[a-f0-9]{40}$/.test(value))
}

function proposalOf(value) {
  if (record(value) && Object.keys(value).length === 2 &&
      Object.hasOwn(value, 'action') && Object.hasOwn(value, 'revision') &&
      rules.has(value.action) && revision(value.revision)) {
    return { action: value.action, revision: value.revision }
  }
  return null
}

function receiptIssue(r) {
  if (r.availability !== 'available') return ['missing_evidence', 'receipt_unavailable']
  if (r.execution === 'failed') return ['withhold', 'execution_failed']
  if (r.execution !== 'completed') return ['missing_evidence', 'execution_not_run']
  if (r.semantic === 'failed') return ['withhold', 'semantic_failed']
  if (r.semantic !== 'passed') return ['missing_evidence', 'semantic_not_run']
  return null
}

/** Load the independently pinned source, then bind trusted host callbacks. */
export async function controllerFactory(upstreamPath) {
  const source = await readFile(upstreamPath)
  if (createHash('sha256').update(source).digest('hex') !== upstreamHash) {
    throw new Error('B-Tests gate digest differs from the frozen pin')
  }
  const { evaluateAction } = await import('data:text/javascript;base64,' + source.toString('base64'))

  function evaluate(proposal, state) {
    const selected = { report: null, grant: null }
    const verdict = (decision, code, { receiptIds = [], missing = [], scope = null } = {}) =>
      ({ decision, code, selected: { ...selected }, receiptIds, missing, scope })
    const withhold = (code, detail) => verdict('withhold', code, detail)
    const missing = (code, need) => verdict('missing_evidence', code, { missing: [need] })

    if (!proposal) return withhold('invalid_proposal')
    if (state == null) return missing('state_unavailable', 'host_state')
    if (!validState(state)) return missing('invalid_state', 'valid_host_state')
    const { action, revision: target } = proposal
    const key = action + ':' + target
    const grants = state.grants.filter(g => g.issuer === 'maintainer' && g.session === state.session.id)
    const coreState = {
      revision: state.revision,
      direction: { id: 'host-direction', grants: grants.map(({ action, revision }) => ({ action, revision })) },
      requirements: { [action]: [] },
      checks: [],
    }
    const authorization = evaluateAction(proposal, coreState)
    if (authorization.code === 'revision_mismatch') return withhold(authorization.code)
    if (state.session.role !== 'Betty' || !state.session.capabilities.includes(action)) {
      return withhold('capability_denied')
    }
    if (state.used.includes(key)) return withhold('duplicate_request')

    const reports = state.reports.filter(r => r.kind === 'applied' && r.revision === target)
    if (!reports.length) return missing('report_missing', 'current_applied_report')
    if (reports.length > 1) return withhold('report_conflict')
    selected.report = reports[0].id
    if (!authorization.allowed) return withhold(authorization.code)
    const grant = grants.find(g => g.action === action && g.revision === target)
    selected.grant = grant.id
    if (grant.status === 'revoked') return withhold('grant_revoked')

    const [phase, checks] = rules.get(action)
    if (state.release !== phase) return withhold('release_phase_mismatch')
    if (state.custody === 'unavailable') return missing('custody_unavailable', 'public_custody')
    if (state.custody !== 'public') return withhold('custody_restricted')

    const scoped = state.receipts.filter(r => r.action === action && r.revision === target && requiredBy(action, r.kind))
    coreState.requirements[action] = checks
    coreState.checks = scoped.map(r => ({
      id: r.id, revision: target, check: r.kind, status: receiptIssue(r) ? 'failed' : 'passed',
    }))
    const result = evaluateAction(proposal, coreState)
    if (result.code === 'missing_check') return missing(result.code, result.check)
    if (result.code === 'ambiguous_check') {
      return withhold(result.code, { receiptIds: scoped.filter(r => r.kind === result.check).map(r => r.id) })
    }
    if (result.code === 'check_not_passed') {
      const [decision, code] = receiptIssue(scoped.find(r => r.id === result.receiptId))
      return verdict(decision, code, { receiptIds: [result.receiptId],
        missing: decision === 'missing_evidence' ? [result.check] : [] })
    }
    if (!result.allowed) return withhold(result.code)
    const mode = action === 'record-canary' ? 'local-canary' : 'shadow'
    return verdict('allow', 'allowed', { receiptIds: result.receiptIds, scope: { action, revision: target, mode } })
  }

  return function createController({ readState, writeCanary, beforeWrite = () => {} }) {
    const reserved = new Set()
    function decide(proposal) {
      if (!proposal) return evaluate(null)
      let state
      try {
        state = readState()
      } catch {
        return evaluate(proposal)
      }
      if (record(state) && Array.isArray(state.used)) {
        state = { ...state, used: [...state.used, ...reserved] }
      }
      return evaluate(proposal, state)
    }
    return Object.freeze({
      evaluate(input) {
        return decide(proposalOf(input))
      },
      run(input) {
        const proposal = proposalOf(input)
        let verdict = decide(proposal)
        if (verdict.scope?.mode !== 'local-canary') return { verdict, execution: 'not_run' }
        try {
          beforeWrite()
          // One synchronous host turn: reread, reserve, then the fixed ref CAS.
          verdict = decide(proposal)
          if (verdict.decision !== 'allow') return { verdict, execution: 'not_run' }
          reserved.add(proposal.action + ':' + proposal.revision)
          writeCanary(verdict.scope)
          return { verdict, execution: 'completed' }
        } catch {
          return { verdict, execution: 'failed' }
        }
      },
    })
  }
}
