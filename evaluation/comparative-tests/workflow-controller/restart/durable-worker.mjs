import { appendFileSync, existsSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { controllerFactory } from '../controller.mjs'
import { bindHost, gitRunner, loadJSON, observe, saveJSON } from './fixture.mjs'
import { reservations } from './reservation.mjs'

const input = loadJSON(process.argv[2])
const { spec, template, upstream, result, options, storePath } = input
const state = bindHost(template, spec, false)
const git = gitRunner(spec.repo, result + '.stdout')
const proposal = { action: 'record-canary', revision: state.revision }
const store = reservations(storePath, proposal.action + ':' + proposal.revision)
const events = []
function event(name) {
  events.push(name)
  appendFileSync(result + '.events', name + '\n')
}

function rendezvous() {
  writeFileSync(join(storePath, 'ready-' + input.lane), '', { flag: 'wx' })
  const pause = new Int32Array(new SharedArrayBuffer(4))
  const deadline = Date.now() + 6000
  while (![1, 2].every(lane => existsSync(join(storePath, 'ready-' + lane)))) {
    if (Date.now() >= deadline) throw new Error('Both reservations did not reach the barrier')
    Atomics.wait(pause, 0, 0, 5)
  }
}

let attempts = 0
let writes = 0
let competingWrites = 0
let storeProblem
let verifiedStatus
const create = await controllerFactory(upstream)
const gate = create({
  readState: () => ({ ...state, revision: git('rev-parse', 'HEAD') }),
  beforeWrite() {
    if (options.competing) {
      git('update-ref', spec.ref, spec.commits.competing, spec.commits.initial)
      competingWrites++
    }
  },
  writeCanary(scope) {
    if (options.barrier) rendezvous()
    try {
      if (!store.claim()) {
        storeProblem = 'collision'
        throw new Error('Reservation already consumed')
      }
    } catch (error) {
      storeProblem ??= 'unavailable'
      throw error
    }
    event('claimed')
    if (options.crash === 'after-claim') process.exit(73)
    event('writer_attempt')
    attempts++
    let gitError
    try {
      git('update-ref', spec.ref, spec.commits.intended, scope.revision)
      writes++
      event('writer_returned')
    } catch (error) {
      gitError = error
    }
    if (options.crash === 'after-git' && !gitError) process.exit(74)
    const ref = observe(git, spec)
    if (!gitError && ref.oid === spec.commits.intended && ref.marker === 'intended') {
      store.finish('completed', ref)
      verifiedStatus = 'completed'
      return
    }
    if (gitError && Number.isInteger(gitError.status) && gitError.status > 0 &&
        ref.oid === spec.commits.competing && ref.marker === 'competing') {
      store.finish('failed', ref)
      verifiedStatus = 'failed'
    }
    throw gitError ?? new Error('The expected ref and marker could not be verified')
  },
})

const prior = store.inspect()
const initialAdmission = gate.evaluate(proposal)
function refuse(decision, code, missing = []) {
  return { ...initialAdmission, decision, code, scope: null, missing }
}
let verdict = initialAdmission
let execution = 'not_run'
let controllerResult
if (initialAdmission.decision === 'allow') {
  if (prior === 'unavailable') {
    verdict = refuse('missing_evidence', 'reservation_unavailable', ['reservation_store'])
  } else if (prior === 'pending') {
    verdict = refuse('missing_evidence', 'reservation_indeterminate', ['verified_prior_outcome'])
  } else if (prior !== 'unused') {
    verdict = refuse('withhold', 'duplicate_request')
  } else {
    controllerResult = gate.run(proposal)
    verdict = controllerResult.verdict
    execution = controllerResult.execution
    if (storeProblem === 'collision') {
      verdict = refuse('withhold', 'reservation_conflict')
      execution = 'not_run'
    } else if (storeProblem === 'unavailable') {
      verdict = refuse('missing_evidence', 'reservation_unavailable', ['reservation_store'])
      execution = 'not_run'
    } else if (execution !== 'not_run' && verifiedStatus === undefined) {
      execution = 'indeterminate'
    }
  }
}
saveJSON(result, {
  pid: process.pid, proposal, initialAdmission, controllerResult, verdict, execution,
  attempts, writes, competingWrites, prior, store: storeProblem === 'collision' ? 'contended' : store.inspect(),
  events, ref: observe(git, spec),
})
