"""Prepare Bastet's deterministic printed-writer selection pairs."""
import argparse
import hashlib
from pathlib import Path

from tools.cryptid_packet_support_v4 import key, packet
from tools.cryptid_trial_v5 import read, save, sha

HOME = Path(__file__).resolve().parent
ROOT = HOME.parents[2]
TITLE = 'Synthetic documentary record'
QUALIFIER = 'Source-scoped reporting statement only; retain its denial and conditions. Independent authorship, reporting occurrence and execution remain unverified.'


def item(role, reporter, author, obj, *, byline='Written by', withdraw=False, ident='SYN-A'):
    end = '' if byline == 'From:' else '.'
    label = f'{byline} {role}{end}'
    clause = f'{reporter} reported that {author} wrote {obj}.'
    return dict(id=ident, title=TITLE, origin='machine', external='yes', withdraw=withdraw,
                when='2026-11-27T00:00Z', body_html=f'<p>{label}</p><p>{clause}</p>'), (label, clause)


def witnesses(source, lines):
    body='\n'.join(lines)
    headed=f'<h1>{TITLE}</h1>\n'+source['body_html']
    digest=hashlib.sha256(headed.encode()).hexdigest()
    result=[]
    for line in lines:
        start=body.index(line)
        offset=len(headed[:headed.index(line)].encode())
        result.append(dict(source_id=source['id'],quote=line,body_start=start,
                           body_end=start+len(line),start_byte=offset,
                           end_byte=offset+len(line.encode()),body_html_sha256=digest))
    return result


def draw(phase):
    if phase=='development':
        writer, reporter, author, other = 'Dina Wood', 'Elin Day', 'Nell Marsh', 'Wade Knox'
        obj, alternative = 'the trail inventory', 'the supply note'
        question = lambda name, voice: f'In the report written by {name}, what did {voice} report that {author} wrote?'
        byline='Written by'
    else:
        writer, reporter, author, other = 'Vale Hill', 'Nora Penn', 'Lyle Park', 'Wren West'
        obj, alternative = 'the workshop roster', 'the visitor checklist'
        question = lambda name, voice: f'What did {voice} say {author} wrote, in the document from {name}?'
        byline='From:'
    common = dict(reporter=reporter, author=author, byline=byline)
    original, lines = item(writer,obj=obj,**common)
    duplicate, _ = item(writer,obj=alternative,ident='SYN-B',**common)
    retired = dict(duplicate,withdraw=True)
    missing = dict(original, body_html=f'<p>{lines[1]}</p>')
    quote = dict(missing, body_html=missing['body_html']+f'<blockquote><p>{lines[0]}</p></blockquote>')
    second_byline=f'{byline} {other}' + ('' if byline=='From:' else '.')
    contradictory = dict(original, body_html=f'<p>{lines[0]}</p><p>{second_byline}</p><p>{lines[1]}</p>')
    other_voice, other_lines = item(writer,other,author,alternative,byline=byline)
    swapped_voice, swapped_lines = item(writer,author,other,obj,byline=byline)

    def positive(source, lines, voice, actor, text):
        expected = key('complete', dict(reporter=voice,author=actor,object=text,
            source_writer_or_unknown=writer, outer_negative=False, embedded_content_negative=False,
            actual_authorship_established=False, source_voice='source_reports_named_speaker'),
            lines, qualifiers=(QUALIFIER,))
        expected['io'] = dict(kind='supported_answer',missing=[],diagnostic='supported',
                             selected_source=source['id'],witnesses=witnesses(source,lines))
        return expected

    def negative(reason, *, selected=None):
        expected=key('withhold')
        expected['io']=dict(kind='abstain', missing=[], diagnostic='record_observed_code',
                            selected_source=selected, selection_or_proof_obligation=reason,
                            witnesses=[])
        return expected

    named=question(writer,reporter)
    main_claim=positive(original,lines,reporter,author,obj)
    other_claim=positive(other_voice,other_lines,other,author,alternative)
    swapped_claim=positive(swapped_voice,swapped_lines,author,other,obj)
    quoted_distractor=dict(original,body_html=original['body_html']+f'<blockquote><p>{second_byline}</p></blockquote>')
    quote_claim=positive(quoted_distractor,lines,reporter,author,obj)
    altered=question(writer,author).replace(f'{author} wrote',f'{other} wrote')
    for question_text, sources, expected, family in (
        (named, [original], main_claim, 'printed-writer'),
        (named, [missing], negative('missing_printed_writer'), 'printed-writer'),
        (question(writer,other), [other_voice], other_claim, 'separate-reporter'),
        (question(writer,writer), [other_voice], negative('writer_does_not_become_reporter', selected='SYN-A'), 'separate-reporter'),
        (named, [original,retired], main_claim, 'eligible-uniqueness'),
        (named, [original,duplicate], negative('competing_eligible_paths'), 'eligible-uniqueness'),
        (named, [quoted_distractor], quote_claim, 'quoted-label'),
        (named, [quote], negative('writer_label_in_quote_only'), 'quoted-label'),
        (altered, [swapped_voice], swapped_claim, 'conflicting-byline'),
        (altered, [dict(swapped_voice,body_html=swapped_voice['body_html'].replace(f'<p>{swapped_lines[1]}</p>',f'<p>{second_byline}</p><p>{swapped_lines[1]}</p>'))],
         negative('conflicting_printed_writer_declarations'), 'conflicting-byline'),
        (named, [original,dict(other_voice,id='SYN-C',withdraw=True)], main_claim, 'unsupported-reporter-after-selection'),
        (question(writer,other), [original], negative('requested_reporter_missing_in_selected_source', selected='SYN-A'), 'unsupported-reporter-after-selection'),
    ):
        yield dict(question=question_text,sources=sources,key=expected,
                   mechanism=family,protected_operation='native named writer then exact attributed report',
                   origin={'test':family,'programme':'Egyptian Bastet v1'})


def prepare(private):
    baseline=read(HOME/'baseline.json')
    for phase, suffix in (('development','D'),('fresh','F')):
        folder=HOME/phase
        packet(folder,'BASTET-'+suffix,list(draw(phase)),baseline['commit'],
               str(Path(__file__).relative_to(ROOT)),held=False)
        # The existing packet writer emits an evaluator file. Move it before staging.
        hidden=private/(phase+'-key.json')
        assert not hidden.exists()
        (folder/'key.json').rename(hidden)
        seal=read(folder/'freeze.json')
        seal.update(baseline_runtime_zip_sha256=baseline['runtime_zip_sha256'],
                    phase=phase, key_sha256=sha(hidden), publication='authorized synthetic raw outputs only')
        for path in (HOME/'io_score.py',HOME/'baseline.json',ROOT/'.github/workflows/egyptian-bastet.yml'):
            seal['harness'][str(path.relative_to(ROOT))]=sha(path)
        (folder/'freeze.json').unlink()
        save(folder/'freeze.json',seal)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--custodian',required=True,type=Path)
    prepare(parser.parse_args().custodian.resolve())
