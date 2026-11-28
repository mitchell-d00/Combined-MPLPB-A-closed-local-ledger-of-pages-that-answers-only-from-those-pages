"""Replay the unchanged reader, then separately inspect consumed evidence spans."""
import gzip
import hashlib
import html
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

from mplpb_answers import documentary, documentary_verify, prose_retrieval, reference_identity, relation_graph
from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from tools.historical_study import digest, implementation_pins, read, validate_corpus


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def proposals(record, body, span):
    # Always supply complete original units. A clipped gold quotation may
    # omit attribution or negation and must not become a proof proposal.
    for start, end, text in documentary_verify.units(body, record):
        if not start <= span['start'] < span['end'] <= end:
            continue
        yield {
            'source_id': record.id, 'path': record.path, 'hash': record.hash_actual,
            'start': start, 'end': end, 'quote': text,
        }


def in_span(items, target):
    matches = []
    for item in items:
        origin = item.get('body_start')
        quote = item.get('text', item.get('quote'))
        if item.get('source_id') != target['source_id'] or type(origin) is not int or not isinstance(quote, str):
            continue
        a, b = target['start']-origin, target['end']-origin
        if 0 <= a < b <= len(quote) and quote[a:b] == target['quote']:
            matches.append(item)
    return matches


def run_native(root, question, budgets):
    index = PassageIndex(root, question)
    passages, chars = budgets['passages'], budgets['characters']
    answer = answer_query(root, question, max_passages=passages, max_chars=chars).contract
    relation = relation_graph.parse(question)
    # These are post-answer ranking probes. Strict may never have called
    # either ranker, which is preserved verbatim in its answer contract.
    return {
        'answer': answer,
        'interpretation': {
            'documentary_plan': documentary.plan(question),
            'named_reference_request': reference_identity.parse_request(question),
            'literal_relation_frame': relation.to_dict() if relation else None,
        },
        'eligibility': {'records': [{'id': r.id, 'path': r.path, 'hash': r.hash_actual} for r in index.records],
                        'excluded': index.gate.excluded, 'snapshot': index.gate.corpus_snapshot},
        'passage_index': index.passages,
        'bm25_probe': index.retrieve([question], passages, chars),
        'documentary_prose_probe': prose_retrieval.retrieve(index, passages, chars),
    }


def evidence_readback(root, case, first, targets, corpus, budgets):
    question = case['question']
    index = PassageIndex(root, question)
    records = {r.id:r for r in index.records}
    placements = []
    for span in targets['spans']:
        a, b = span['start'], span['end']
        projected = corpus[span['source_id']][a:b] == span['quote']
        record = records.get(span['source_id'])
        body = body_text(record.body_html) if record else ''
        exact = projected and body[a:b] == span['quote']
        native = first['answer']
        displayed = [*native.get('retrieval', {}).get('passages', []),
                     *(c for claim in native['claims'] for c in claim['citations'])]
        protocols = ['relationship_statement', 'action_statement',
                     'literal_location'] if case['id'].startswith('FRUS01-LOC-') else [
                         'relationship_statement', 'action_statement']
        units = list(proposals(record,body,span)) if exact else []
        submitted = [{**unit, 'kind': kind} for unit in units for kind in protocols]
        assert len(submitted) <= budgets['verifier_proposals_per_anchor']
        kernel = documentary_verify.check(index, submitted, max_scan_chars=budgets['verifier_scan_characters']) if submitted else None
        if kernel:
            kernel = {k:v for k,v in kernel.items() if k not in ('contexts','observations')}
        placements.append({
            'anchor': span, 'projected_exact': projected, 'eligible_exact': exact,
            'native_index_passage_ids': [p['id'] for p in in_span(first['passage_index'], span)],
            'bm25_ranks': [i for i,p in enumerate(first['bm25_probe']['passages'],1) if in_span([p],span)],
            'prose_ranks': [i for i,p in enumerate(first['documentary_prose_probe']['passages'],1) if in_span([p],span)],
            'native_displayed': bool(in_span(displayed,span)),
            'native_units': units, 'submitted': submitted,
            'verifier': kernel,
        })
    return {'id':case['id'], 'expected_obligations': targets['obligations'], 'spans': placements,
            'native_answer_sha256': digest(first['answer'])}


def write_output(path, value):
    with path.open('xb') as stream:
        stream.write(gzip.compress(json.dumps(value,ensure_ascii=False,indent=2).encode()+b'\n', mtime=0))


def main():
    mode, corpus_path, freeze_dir, out_path, *extra = sys.argv[1:]
    directory, corpus_path = Path(freeze_dir), Path(corpus_path)
    pin = read(directory/'freeze.json')
    budgets = pin['budgets']
    assert implementation_pins() == pin['implementation_sha256']
    assert sha(corpus_path) == pin['inputs_sha256']['corpus.json']
    assert sha(directory/'questions.json') == pin['diagnostic_inputs_sha256']['questions.json']
    cases = read(directory/'questions.json')
    corpus = read(corpus_path)
    validate_corpus(corpus)
    before = None
    if mode == 'readback':
        trace_path, target_path = map(Path,extra)
        assert sha(target_path) == pin['diagnostic_inputs_sha256']['consumed-anchors.json']
        with gzip.open(trace_path,'rb') as stream:
            before = json.load(stream)
        assert before['freeze_sha256'] == sha(directory/'freeze.json')
        targets = read(target_path)
        assert [row['id'] for row in before['rows']] == [row['id'] for row in cases]
    else:
        assert mode == 'native' and not extra
    by_id = {source['id']: source['text'] for source in corpus['sources']}
    rows = []
    with TemporaryDirectory(prefix='frus-relationship-') as root:
        for source in corpus['sources']:
            write(root,doc_id=source['id'],title=source['original_path'],
                  scope='original historical document',origin='machine',
                  body_html='<pre>'+html.escape(source['text'])+'</pre>',when=budgets['fixture_time'])
        for i, case in enumerate(cases):
            try:
                row = (run_native(root,case['question'],budgets) if before is None else
                       evidence_readback(root,case,before['rows'][i],targets[case['id']],by_id,budgets))
                rows.append({'id':case['id'],**row})
            except (OSError, ValueError, KeyError) as error:
                rows.append({'id':case['id'],'execution_error': repr(error)})
    assert implementation_pins() == pin['implementation_sha256']
    write_output(Path(out_path),{'mode':mode,'freeze_sha256':sha(directory/'freeze.json'),'rows':rows})


if __name__ == '__main__':
    main()
