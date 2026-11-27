import json
from pathlib import Path
p=Path('evaluation/comparative-tests/workflow-controller')
base='a7d572067dbf68077ea306584b067e457bd7a3a4'
old='a442c8f0c9629b65a3af38ba57319aa9c2af8dbe'
actions={'run-tests':('prepared',['input-freeze']), 'merge':('tested',['candidate-tests','release-acceptance']),
         'deploy':('merged',['merge-event','deployment-package']), 'record-canary':('prepared',['canary-ready'])}
def states(action):
    phase,checks=actions[action]
    return dict(revision=base,session=dict(id='session-1',role='Betty',capabilities=[action]),
        grants=[dict(id='direction-1',issuer='maintainer',session='session-1',action=action,revision=base,status='active')],
        reports=[dict(id='report-1',kind='applied',revision=base)],
        receipts=[dict(id='receipt-'+k,action=action,revision=base,kind=k, availability='available',
                       execution='completed',semantic='passed') for k in checks], custody='public',release=phase,used=[])
def row(id,action,decision,code,edit=None,**extra):
    s=states(action)
    if edit: edit(s)
    proposal=dict(action=action,revision=base)
    proposal.update(extra.pop('proposal_fields',{}))
    return dict(id=id,proposal=proposal,state=s,expect=dict(decision=decision,code=code),**extra)
def set_(key,value): return lambda s:s.update({key:value})
def edit(kind,index,**change): return lambda s:s[kind][index].update(change)
M='missing_evidence'; W='withhold'; A='allow'
dev=[
row('D01','run-tests',A,'allowed'),row('D02','merge',A,'allowed'),row('D03','deploy',A,'allowed'),
row('D04','deploy',W,'revision_mismatch',proposal_fields={'revision':old}),
row('D05','merge',W,'capability_denied',edit('unused',0) if False else lambda s:s['session'].update(role='Al')),
row('D06','merge',W,'not_authorized',edit('grants',0,issuer='Outside')),
row('D07','merge',M,'report_missing',edit('reports',0,revision=old)),
row('D08','merge',M,'missing_check',edit('receipts',0,revision=old)),
row('D09','merge',W,'execution_failed',edit('receipts',0,execution='failed',semantic='not_run')),
row('D10','merge',W,'semantic_failed',edit('receipts',1,semantic='failed')),
row('D11','merge',M,'receipt_unavailable',edit('receipts',1,availability='unavailable')),
row('D12','deploy',W,'release_phase_mismatch',set_('release','tested')),
row('D13','merge',W,'grant_revoked',edit('grants',0,status='revoked')),
row('D14','merge',W,'invalid_proposal',proposal_fields={'session':'maintainer'}),
row('D15','run-tests',M,'custody_unavailable',set_('custody','unavailable')),
]
held=[
row('H01','deploy',M,'missing_check',edit('receipts',0,action='merge')),
row('H02','merge',W,'ambiguous_authorization',lambda s:s['grants'].append(dict(s['grants'][0],id='direction-2',status='revoked'))),
row('H03','deploy',W,'report_conflict',lambda s:s['reports'].extend([dict(id='older',kind='applied',revision=old),dict(id='second',kind='applied',revision=base)])),
row('H04','merge',A,'allowed',lambda s:s['reports'].extend([dict(id='older',kind='applied',revision=old),dict(id='advice',kind='advice',revision=base)])),
row('H05','deploy',M,'execution_not_run',edit('receipts',1,execution='not_run',semantic='passed')),
row('H06','deploy',M,'semantic_not_run',edit('receipts',1,semantic='not_run')),
row('H07','merge',M,'invalid_state',lambda s:s.pop('custody')),
row('H08','run-tests',W,'custody_restricted',set_('custody','restricted')),
row('H09','deploy',W,'ambiguous_check',lambda s:s['receipts'].append(dict(s['receipts'][0],id='conflict',semantic='failed'))),
row('H10','deploy',W,'not_authorized',edit('grants',0,session='another-session')),
]
archive='https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages'
shadow=[
row('S01','merge',W,'semantic_failed',edit('receipts',1,semantic='failed'),observed='withhold',record='Original PR110 87/96 exact gate failed', source=archive+'/pull/110'),
row('S02','merge',A,'allowed',observed='allow',record='PR110 authorized nine-case prospective pass and merged',source=archive+'/pull/110#issuecomment-7219742999'),
row('S03','deploy',A,'allowed',observed='allow',record='PR110 merged then Pages published',source=archive+'/actions/runs/46008844245'),
row('S04','run-tests',M,'custody_unavailable',set_('custody','unavailable'),observed='withhold',record='17 original checks incomplete and 100 held cases NOT_RUN',source='../cryptid/../full-reproducible-replay/README.md'),
row('S05','run-tests',A,'allowed',observed='allow',record='Exact primary rebuild restored 444 original cases before replay',source='../../cryptid/full-reproducible-replay/README.md'),
row('S06','deploy',M,'missing_check',edit('receipts',0,revision=old),observed='withhold',record='B-Tests Round 7 old revision pass did not admit deploy',source='https://github.com/mitchell-d00/B-Tests/blob/c8f5b90a3560a0c0a916955719cef76074abebf8/gate-js/round-7.json'),
row('S07','merge',W,'execution_failed',edit('receipts',0,execution='failed',semantic='not_run'),observed='withhold',record='D% prelaunch failed before reader ran; no release credit',source='../../cryptid/full-reproducible-replay/README.md'),
]
shadow[3]['source']='../../cryptid/full-reproducible-replay/README.md'
canary=[
dict(id='C01',scenario='blocked-role',expect='capability_denied',effect=False),
dict(id='C02',scenario='wrong-revision',expect='revision_mismatch',effect=False),
dict(id='C03',scenario='stale-receipt',expect='missing_check',effect=False),
dict(id='C04',scenario='conflicting-receipts',expect='ambiguous_check',effect=False),
dict(id='C05',scenario='revoked-grant',expect='grant_revoked',effect=False),
dict(id='C06',scenario='revoke-before-write',expect='grant_revoked',effect=False),
dict(id='C07',scenario='allow',expect='allowed',effect=True),
dict(id='C08',scenario='duplicate',expect='duplicate_request',effect=False),
]
for name,rows in [('development',dev),('shadow',shadow),('held',held)]:
    (p/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
(p/'canary.json').write_text(json.dumps({'template':states('record-canary'),'cases':canary},indent=2)+'\n')
