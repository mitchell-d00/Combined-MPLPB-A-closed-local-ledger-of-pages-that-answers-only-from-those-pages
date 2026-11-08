"""Exercise the local adapter with the optional official MCP Python SDK.

Run with mcp==1.26.0 installed in a separate test environment; not a runtime
server dependency, model-provider test or independent human evaluation.
"""
import argparse
import asyncio
from importlib.metadata import version
import json
import hashlib
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from mplpb_combined.ledger import write, revise, withdraw


async def run():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append({'check': name, 'passed': True})
    async def call(session, name, args=None):
        response = await session.call_tool(name, args or {})
        check('tool result is successful: '+name, not response.isError)
        data = response.structuredContent
        check('legacy text preserves complete structured result: '+name, json.loads(response.content[0].text) == data)
        return data
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder);root = base/'ledger';root.mkdir()
        write(root,doc_id='ITEM-001',title='Synthetic receiver',scope='Vexel receiver channel',body='The Vexel receiver channel is 5271.')
        procedure={'id':'align-quillon','steps':[
            {'order':1,'action':'Place the sample in amber cradle.','prerequisites':[],'conditions':['Only while the sample is dry.'],'warnings':['Stop if the sample cracks.']},
            {'order':2,'action':'Close the latch.','prerequisites':[1],'conditions':['Wait until the edges align.'],'warnings':['Do not force the latch.']}]}
        body='MPLPB-PROCEDURE/1 '+json.dumps(procedure)
        write(root,doc_id='PLAN-001',title='Synthetic instructions',scope='align quillon procedure',body=body)
        params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'tools/mplpb_mcp.py'),'--data-dir',str(base/'state'),'--ledger','notes='+str(root),'--profile','internal'])
        async with stdio_client(params) as (reader,writer):
            async with ClientSession(reader,writer) as session:
                initialized=await session.initialize()
                check('protocol negotiated',initialized.protocolVersion == '2025-06-18')
                tools=await session.list_tools()
                check('all tools discoverable',len(tools.tools)==7)
                status=await call(session,'mplpb_status')
                check('host-fixed profile and offline boundary',status['profile']=='internal' and not status['network'])
                collections=await call(session,'mplpb_collections')
                check('only authorized collection visible',[c['corpus'] for c in collections['collections']]==['notes'])
                q={'corpus':'notes','question':'What is the Vexel receiver channel?'}
                answer=await call(session,'mplpb_ask',q)
                check('strict supported answer with exact source value',answer['decision']['answer_supported'] and '5271' in answer['reply'])
                pages=await call(session,'mplpb_pages',{'corpus':'notes'})
                page=next(p for p in pages['pages'] if p['id']=='ITEM-001')
                source=await call(session,'mplpb_read_page',{'corpus':'notes','path':page['path']})
                check('citation hash matches inspected source',source['page']['hash']==answer['decision']['hash'])
                check('inspection is not answer support',source['answer_supported'] is False)
                first=await call(session,'mplpb_chat',{'corpus':'notes','message':'How do I align quillon?'})
                sid=first['session']
                check('procedure source conditions and exact quotation survive','Only while' in first['reply'] and first['response']['procedure']['steps'][0]['source']['quote']==body)
                pending=await call(session,'mplpb_chat',{'corpus':'notes','message':'show warnings','session':sid})
                check('focused clarification asks for step',pending['kind']=='clarify' and 'Which step' in pending['reply'])
        async with stdio_client(params) as (reader,writer):
            async with ClientSession(reader,writer) as session:
                await session.initialize()
                saved=await call(session,'mplpb_session',{'session':sid,'limit':1})
                check('session resumes after a real process restart',saved['chain_intact'] and saved['next_offset']==1)
                recovered=await call(session,'mplpb_chat',{'corpus':'notes','message':'step 2','session':sid})
                check('pending warning selection recovers','Do not force' in recovered['reply'] and recovered['response']['requested_constraint']=='warnings')
                corrected=await call(session,'mplpb_chat',{'corpus':'notes','message':'No, I meant step 1','session':sid})
                check('explicit correction recovers intended step','amber cradle' in corrected['reply'])
                next_step=await call(session,'mplpb_chat',{'corpus':'notes','message':'next step','session':sid})
                check('execution is not inferred',next_step['kind']=='clarify')
                denied=await session.call_tool('mplpb_ask',dict(q,profile='lab'))
                check('client cannot replace host profile',denied.isError)
                revise(root,'ITEM-001',body='The Vexel receiver channel is 8463.')
                changed=await call(session,'mplpb_ask',q)
                check('changed source value changes answer','8463' in changed['reply'] and '5271' not in changed['reply'])
                write(root,doc_id='DENY-001',title='Synthetic denial',scope='Vexel receiver channel',body='The Vexel receiver channel is not 8463.')
                conflict=await call(session,'mplpb_ask',q)
                check('contradiction prevents unqualified answer',not conflict['decision']['answer_supported'] and conflict['kind']=='ambiguous')
                withdraw(root,'DENY-001')
                refusal=await call(session,'mplpb_ask',{'corpus':'notes','question':'Who manufactured the Vexel receiver?'})
                check('missing relationship refuses',not refusal['decision']['answer_supported'])
    return {'role':'Authored MCP protocol and workflow acceptance; no model/provider or independent human validation',
            'sdk':{'package':'mcp','version':version('mcp')},
            'implementation': {'python': sys.version.split()[0], 'adapter_sha256': hashlib.sha256((ROOT/'tools/mplpb_mcp.py').read_bytes()).hexdigest(),
                               'client_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'checks':checks,'passed':len(checks),
            'limitations':['Tests the SDK as a protocol client, not a third-party AI application or model obedience.',
                           'Existing finite reader and trusted local operator scope remain in force.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.output and args.output.exists():parser.error('Choose a new output file; preserve previous runs')
    data=asyncio.run(run());payload=json.dumps(data,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(payload)
    print(payload,end='')


if __name__=='__main__':main()
