import { controllerFactory } from '../controller.mjs'
import { bindHost, gitRunner, loadJSON, observe, saveJSON } from './fixture.mjs'

const input = loadJSON(process.argv[2])
const { spec, template, upstream, hostUsed, competing, result } = input
const state = bindHost(template, spec, hostUsed)
const git = gitRunner(spec.repo, result + '.stdout')
const proposal = { action: 'record-canary', revision: state.revision }
let attempts = 0
let writes = 0
let competingWrites = 0
const create = await controllerFactory(upstream)
const gate = create({
  readState: () => ({ ...state, revision: git('rev-parse', 'HEAD') }),
  beforeWrite() {
    if (competing) {
      git('update-ref', spec.ref, spec.commits.competing, spec.commits.initial)
      competingWrites++
    }
  },
  writeCanary(scope) {
    attempts++
    git('update-ref', spec.ref, spec.commits.intended, scope.revision)
    writes++
  },
})
const initialAdmission = gate.evaluate(proposal)
const resultOfRun = gate.run(proposal)
const subsequent = gate.evaluate(proposal)
saveJSON(result, {
  pid: process.pid, proposal, hostUsed, initialAdmission, ...resultOfRun, subsequent,
  attempts, writes, competingWrites, ref: observe(git, spec),
})
