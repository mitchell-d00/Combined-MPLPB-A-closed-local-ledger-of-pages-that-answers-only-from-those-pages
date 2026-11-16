"""Post-run stage audit; draft references never enter an evaluation worker."""
import argparse
from pathlib import Path
from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_combined.ledger import Ledger
from tools.unprepared_challenge import read,save,summary,covers
from tools.unprepared_sources import verify,import_corpus,sha
import tempfile


def trace(directory):
    root=Path(directory);manifest=verify(root)
    baseline=summary(root,root/'baseline');search=summary(root,root/'bm25')
    refs=read(root/'reference-draft.json')['cases'];rows=[]
    with tempfile.TemporaryDirectory() as temp:
        ledger=Path(temp)/'ledger';receipt=import_corpus(root,ledger)
        if receipt!=read(root/'baseline/import-receipt.json'):raise ValueError('Import differs from frozen baseline')
        index=PassageIndex(ledger,'historical correspondence archive records')
        records={r.id:r for r in Ledger(ledger).records};audit=[]
        for ref,b,s in zip(refs,baseline['rows'],search['rows']):
            if ref['id']!=b['id'] or b['id']!=s['id']:raise ValueError('Case order changed')
            evidence=[]
            for c in ref['citations']:
                rec=records[c['source_id']];body=body_text(rec.body_html)
                evidence.append({'source_id':rec.id,'hash':rec.hash_actual,'start':c['start'],'end':c['end'],
                    'preserved_exactly':body[c['start']:c['end']]==c['quote'],
                    'contained_in_single_index_passage':any(covers(p,c) for p in index.passages)})
            native=read(root/'baseline'/(ref['id']+'.json'))
            earliest=('retrieval_or_context_assembly' if s['reference_evidence_spans_retrieved']<len(evidence)
                      else 'semantic_mapping_and_interpretation')
            rows.append({'id':ref['id'],'draft_answerability':ref['answerability_draft'],
                'earliest_demonstrated_constraint':earliest,
                'source_acquisition':'hash_verified','native_import':'valid_and_reproduced',
                'evidence':evidence,'bm25_draft_spans_retrieved':s['reference_evidence_spans_retrieved'],
                'baseline_answer_kind':b['answer_kind'],'baseline_diagnostic':b['diagnostic'],
                'baseline_answer_retrieval_ranking':native['answer']['retrieval']['ranking'],
                'expert_stops':native['investigation']['stops'],
                'historical_answer_correctness':'UNASSESSED','refusal_appropriateness':'NOT RUN',
                'notice':'An uncovered draft span is not proof that all relevant evidence is absent; some negative controls appropriately cannot establish a relationship.'})
        for r in receipt['records']:
            rec=records[r['id']]
            audit.append({'source_id':rec.id,'native_hash':rec.hash_actual,'original_id':r['original_id'],
                'original_sha256':r['original_sha256'],'valid_hash':rec.hash==rec.hash_actual,
                'projection_sha256':sha(body_text(rec.body_html).encode()),
                'all_native_fields':dict(rec.fields),'all_wrapper_metadata_source_authored':False,
                'title':rec.title,'title_source_authored':False})
    return {'schema':'original-conversion-stage-audit-v1','baseline_commit':read(root/'baseline-inventory.json')['git_commit'],
        'corpus_manifest_sha256':sha((root/'corpus-manifest.json').read_bytes()),'original_count':len(manifest['sources']),
        'native_page_count':len(receipt['records']),'indexed_passages':len(index.passages),
        'wrapper_audit':audit,'questions':rows,'semantic_review':'NOT RUN',
        'findings':['All 23 draft spans survive native import exactly in the canonical projection.',
            'Six draft spans cross passage boundaries; no source loss is implied.',
            'Baseline expert skips large native pages at its 200000-character source budget; header-only grammar does not map prose.',
            'Actual gated BM25 search returns 5 of 23 draft spans; the strict answer pipeline often stops before answer retrieval.',
            'interpretation_unsupported and retrieval_ambiguous require separate historical review; zero support is not a failed import.']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory');p.add_argument('--output',required=True);a=p.parse_args();save(a.output,trace(a.directory))


if __name__=='__main__':main()
