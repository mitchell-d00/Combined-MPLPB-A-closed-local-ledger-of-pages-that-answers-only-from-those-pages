/**
 * Heka-01 laboratory worker. The study driver supplies a disposable Git and
 * ledger fixture. The original controller exposes only its fixed canary effect.
 */
import assert from 'node:assert/strict'
import { join } from 'node:path'
import { controllerFactory } from '../../comparative-tests/workflow-controller/controller.mjs'
import { bindHost, gitRunner, loadJSON, observe, saveJSON } from '../../comparative-tests/workflow-controller/restart/fixture.mjs'
import { reservations } from '../../comparative-tests/workflow-controller/restart/reservation.mjs'
import { nativeStatus, reader, sha } from './study.mjs'

const hash = value => sha(JSON.stringify(value))
const relation = 'source_attributed_report_content'
const action = 'record-canary'

function exactSlice(value, start, end) {
  if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) ||
      start < 0 || end <= start || end > value.length) return null
  return value.slice(start, end).toString()
}

function verifies(raw, obligation) {
  const { answer, selected, snapshot } = raw
  const selection = answer.documentary_support?.named_source_selection
  if (nativeStatus(raw) !== 'complete' || answer.documentary_support?.scope !== relation ||
      selection?.status !== 'verified' || selection.source_id !== obligation.source_id ||
      selected?.id !== obligation.source_id || selected.intact !== true || selected.hash !== selection.hash ||
      selected.bytes_sha256 !== snapshot[selection.path] || answer.claims?.length !== 1) return false
  const [claim] = answer.claims
  const p = claim.proposition
  if (claim.source_support_established !== true || p?.relation !== relation ||
      p.source_writer_or_unknown !== obligation.writer || p.reporter !== obligation.reporter ||
      p.author !== obligation.author || p.object !== obligation.object || p.inner_action !== 'write' ||
      p.content_asserted_by_reporter !== true || p.inner_negative !== false || p.outer_negative !== false ||
      p.actual_authorship_established !== false || p.completion_established !== false ||
      p.conditions?.length !== 0 || claim.citations?.length !== 2) return false
  const html = Buffer.from(selected.body_html)
  const bodyDigest = sha(html)
  return claim.citations.every(c => {
    const w = c.original_witness
    return c.source_id === selection.source_id && c.path === selection.path && c.hash === selection.hash &&
      c.body_projection === 'body-text-no-headings-v1' &&
      exactSlice(selected.body_text, c.body_start, c.body_end) === c.quote &&
      w?.coordinate_space === 'admitted_record_body_html_utf8' &&
      w.body_html_sha256 === bodyDigest && exactSlice(html, w.start_byte, w.end_byte) === c.quote
  })
}

function bindEvidence(raw, obligation, question, readerPin, target) {
  return { schema: 'heka-proof-binding-v1', readerPin, question, obligation,
    snapshot: hash(raw.snapshot), proof: hash(raw.answer), target }
}

async function main(input) {
  const { spec, upstream, lane, ledger, caseFile, storePath, phase, readerPin, result } = input
  const record = loadJSON(caseFile)
  const { scenario, question, obligation } = record
  const template = loadJSON(new URL('../../comparative-tests/workflow-controller/canary.json', import.meta.url))
  const state = bindHost(template.template, spec, false)
  assert.equal(spec.ref, 'refs/heads/canary')
  const git = gitRunner(spec.repo, join(lane, 'git.stdout'))
  const proposal = { action, revision: scenario === 'wrong-target' ? spec.commits.competing : state.revision }
  const target = { action, ref: spec.ref, revision: state.revision,
    intended: spec.commits.intended, namespace: storePath }
  const store = reservations(storePath, action + ':' + state.revision)
  const probe = name => {
    const raw = reader('probe', ledger, caseFile)
    saveJSON(join(lane, name + '-proof.json'), raw)
    return raw
  }
  const trace = { pid: process.pid, authority: input.authority, proposal, target,
    proof: null, recheck: null, attempts: 0, writes: 0, competingWrites: 0, binding: null }
  function report(code, execution = 'not_run') {
    saveJSON(result, { ...trace, code, execution })
  }

  if (trace.authority === 'advice' || trace.authority === 'absent') {
    state.grants = []
    if (trace.authority === 'advice') state.reports.push({ id: 'al-advice', kind: 'advice', revision: state.revision })
  }
  const initial = probe('initial')
  trace.proof = nativeStatus(initial)
  if (!verifies(initial, obligation)) return report('proof_incomplete')
  const expected = bindEvidence(initial, obligation, question, readerPin, target)
  const binding = scenario === 'wrong-receipt'
    ? { ...expected, target: { ...target, revision: spec.commits.competing } }
    : expected
  trace.binding = binding
  if (hash(binding) !== hash(expected)) return report('receipt_binding_mismatch')
  const proofReceipt = { ...state.receipts[0], id: 'heka-' + hash(binding) }
  let active = proofReceipt
  let rejection
  let durableVerdict
  const create = await controllerFactory(upstream)
  const gate = create({
    readState() {
      return { ...state, revision: git('rev-parse', 'HEAD'), receipts: active ? [active] : [] }
    },
    beforeWrite() {
      if (scenario === 'revoked') {
        state.grants[0].status = 'revoked'
        trace.authority = 'revoked'
      }
      if (['withdraw-between', 'unrelated-change'].includes(scenario)) reader('change', ledger, caseFile)
      const fresh = probe('reread')
      trace.recheck = nativeStatus(fresh)
      if (!verifies(fresh, obligation) || hash(bindEvidence(fresh, obligation, question, readerPin, target)) !== hash(binding)) {
        active = null
        rejection = 'evidence_changed'
        return
      }
      if (scenario === 'restart-failed') {
        git('update-ref', spec.ref, spec.commits.competing, spec.commits.initial)
        trace.competingWrites++
      }
    },
    writeCanary(scope) {
      assert.deepEqual(scope, { action, revision: target.revision, mode: 'local-canary' })
      try {
        if (!store.claim()) {
          rejection = 'reservation_conflict'
          throw new Error('Consumed reservation')
        }
      } catch (error) {
        rejection ??= 'reservation_unavailable'
        throw error
      }
      trace.attempts++
      let error
      try {
        git('update-ref', spec.ref, spec.commits.intended, scope.revision)
        trace.writes++
      } catch (caught) {
        error = caught
      }
      trace.workerReadback = observe(git, spec)
      if (scenario === 'restart-interrupted' && phase === 1 && !error) {
        saveJSON(join(lane, 'pre-interruption.json'), trace)
        process.exit(74)
      }
      const ref = trace.workerReadback
      if (!error && ref.oid === spec.commits.intended && ref.marker === 'intended') {
        store.finish('completed', ref)
        durableVerdict = 'completed'
        return
      }
      if (error?.status > 0 && ref.oid === spec.commits.competing && ref.marker === 'competing') {
        store.finish('failed', ref)
        durableVerdict = 'failed'
      }
      throw error ?? new Error('Unverified Git effect')
    },
  })

  const admitted = gate.evaluate(proposal)
  trace.admission = admitted
  if (admitted.decision !== 'allow') {
    return report(admitted.code === 'not_authorized' ? 'grant_missing' : admitted.code)
  }
  const prior = store.inspect()
  trace.prior = prior
  if (prior === 'pending') return report('reservation_indeterminate')
  if (prior === 'unavailable') return report('reservation_unavailable')
  if (prior !== 'unused') return report('duplicate_request')
  const executed = gate.run(proposal)
  trace.controller = executed
  if (rejection) return report(rejection)
  if (executed.execution === 'not_run') return report(executed.verdict.code)
  report(executed.verdict.code, durableVerdict ?? 'indeterminate')
}

await main(loadJSON(process.argv[2]))
