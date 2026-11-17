"""Run these newly authored fictional cases against a pinned full MPLPB checkout.

Usage from the upstream repository root:
python /path/to/reproduce_upstream.py

The fixture folder 'fresh_source_fixture' must be alongside this script.
No network, models, or system writes except temporary graph files are needed.
"""
from pathlib import Path
import subprocess,sys,os,tempfile,json

fixture=Path(__file__).resolve().parent/'fresh_source_fixture'
assert fixture.is_dir(), 'Missing source fixture folder'

def run(*args):
    p=subprocess.run([sys.executable,'-m','mplpb_work.sorter',*map(str,args)],capture_output=True,text=True)
    if p.returncode!=0:
        raise RuntimeError(f"Sorter returned {p.returncode}: {p.stdout}\n{p.stderr}")
    return p

with tempfile.TemporaryDirectory(prefix='mplpb-independent-sorter-') as tmp:
    tmp=Path(tmp);a=tmp/'not_compared.json';b=tmp/'compared.json'
    run('sort',fixture,'--mode','not-compared','--output',a)
    run('sort',fixture,'--mode','compare','--output',b)
    run('verify',b,'--sources',fixture)
    x=json.loads(a.read_text()); y=json.loads(b.read_text())
    checks={
      'same_sources':x['sources']==y['sources'],
      'same_nodes':x['nodes']==y['nodes'],
      'raw_edge_prefix_unchanged':x['edges']==y['edges'][:len(x['edges'])],
      'added_edges_all_review_only':all(e.get('comparison_only') and not e['assessment']['answer_supported'] for e in y['edges'][len(x['edges']):]),
      'all_nodes_unsupported':all(not n['assessment']['answer_supported'] for n in y['nodes']),
      'no_transitive_paths':not y['transitive_paths_generated'],
      'byte_spans_round_trip':all((fixture/n['span']['path']).read_bytes()[n['span']['byte_start']:n['span']['byte_end']].decode('utf-8')==n['span']['text'] for n in y['nodes'] if 'text' in n['span'])
    }
    names={n['id']:n for n in y['nodes']};clusters=[e for e in y['edges'] if e['kind']=='candidate_identity_cluster']
    quoted_clusters=[e for e in clusters if any(names[m]['span']['path']=='07-quoted-header.md' for m in e.get('members',[]))]
    ambiguous=[e for e in y['edges'] if e['kind']=='unresolved_reference_review' and e.get('reason')=='ambiguous_identifier']
    missing=[e for e in y['edges'] if e['kind']=='unresolved_reference_review' and e.get('reason')=='missing_or_outside_budget']
    checks.update({
      'quoted_header_in_unverified_cluster':bool(quoted_clusters),
      'changed_bodies_flagged':any(e.get('changed_bodies') for e in clusters),
      'ambiguous_correction_target_unresolved':bool(ambiguous),
      'missing_correction_target_unresolved':bool(missing)
    })
    print(json.dumps({'upstream_run':True,'checks':checks,'all_checks_true':all(checks.values()),
                      'sources':len(y['sources']),'nodes':len(y['nodes']),'raw_edges':len(x['edges']),
                      'compare_edges':len(y['edges']),'extra_edge_kinds':sorted({e['kind'] for e in y['edges'][len(x['edges']):]})},indent=2))
    assert all(checks.values()),'One or more hypotheses did not hold'
