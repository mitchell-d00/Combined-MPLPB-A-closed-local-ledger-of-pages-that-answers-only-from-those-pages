import { createHash } from 'node:crypto'

export const sha = bytes => createHash('sha256').update(bytes).digest('hex')

export function canonical(value) {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']'
  if (value !== null && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map(key =>
      JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}'
  }
  return JSON.stringify(value)
}

function exactCitation(citation, raw) {
  const source = raw.originals[citation.path]
  if (!source || !source.intact || source.id !== citation.source_id || source.hash !== citation.hash ||
      source.bytes_sha256 !== raw.snapshot[citation.path] ||
      citation.body_projection !== 'body-text-no-headings-v1') return false
  const chars = Array.from(source.body_text)
  const start = citation.body_start
  const end = citation.body_end
  return Number.isSafeInteger(start) && Number.isSafeInteger(end) && start >= 0 &&
    start < end && end <= chars.length && chars.slice(start, end).join('') === citation.quote
}

/** Project one verified native instruction. This function has no grant input. */
export function project(raw, question, reader) {
  const { answer } = raw
  const support = answer.documentary_support
  const complete = answer.kind === 'supported_answer'
  const partial = answer.kind === 'partial_answer'
  if ((!complete && !partial) || answer.answer_supported !== complete ||
      support?.scope !== 'source_attributed_instruction' || support.original_question !== question ||
      support.profile !== 'internal' || answer.source_assurance?.outside_world_truth !== 'not_established' ||
      answer.claims.length !== 1 || support.obligations?.length !== 2) return null

  const [claim] = answer.claims
  const p = claim.proposition
  const [instruction, dateRole] = support.obligations
  if (!claim.source_support_established || p.relation !== 'source_attributed_instruction' ||
      typeof p.writer !== 'string' || typeof p.actor !== 'string' ||
      typeof p.recipient !== 'string' || typeof p.task !== 'string' ||
      p.polarity !== 'affirmative' || p.modality !== 'instruction_only' ||
      !Array.isArray(p.conditions) || p.conditions.length !== 0 ||
      p.completion_established !== false || p.historical_truth_independently_verified !== false ||
      canonical(p.reporting_chain) !== canonical([
        { role: 'document_writer', actor: p.writer },
        { role: 'attributed_instructor', actor: p.actor },
      ]) ||
      instruction.kind !== 'source_attributed_instruction' || instruction.status !== 'supported_source_assertion' ||
      canonical(instruction.evidence_claim_indices) !== '[0]' || dateRole.kind !== 'instruction_date' ||
      claim.citations.length < 2 || !claim.citations.every(c => exactCitation(c, raw)) ||
      new Set(claim.citations.map(c => c.path)).size !== 1) return null

  if (complete && (typeof p.instruction_date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(p.instruction_date) ||
      dateRole.status !== 'supported_source_assertion' || canonical(dateRole.evidence_claim_indices) !== '[0]' ||
      answer.missing.length !== 0)) return null
  if (partial && ('instruction_date' in p || dateRole.status !== 'unresolved' ||
      canonical(dateRole.evidence_claim_indices) !== '[]' || answer.missing.length !== 1 ||
      !answer.missing[0].startsWith('Instruction date:'))) return null

  return {
    schema: 'instruction-source-assertion-v1', status: 'source_assertion', truth: 'unverified',
    execution: 'unverified', question, reader, profile: 'internal', native_kind: answer.kind, claim,
    date: { status: complete ? 'checked' : 'unresolved', value: p.instruction_date ?? null },
    missing: answer.missing, source_revisions: raw.snapshot, obligations: support.obligations,
  }
}
