"""Freeze explicit local-reference tests before native changes."""
from tools.cryptid_packet_support import programme,key

def build(held=False):
    rows=[];name='Leona Silva' if held else 'Mara Flint';other='Ivo Calder';source='DOCUMENT-1'
    refs=[('initials','LS' if held else 'MF'),('surname','Silva' if held else 'Flint'),('title','Director'),('pronoun','she'),('documentary reference','the author')]
    for kind,ref in refs:
        line=(f'The {kind} "{ref}" identifies {name} in this record.' if held else f'{kind.capitalize()} "{ref}" refers to {name}.')
        question=f'Who does "{ref}" identify in source {source}?' if held else f'To whom does "{ref}" refer in source {source}?'
        prop={'relation':'documentary_reference_identity','reference':ref,'referent':name,'source_id':source,'binding':'explicit_reference_gloss'}
        variants=[(line,'complete',{}), (line+' '+line.replace(name,other),'withhold',{}), (f'<blockquote>{line}</blockquote>','withhold',{}),(line,'withhold',{'withdraw':True})]
        if not held:variants += [(f'{ref} wrote the tidal register. Signed: {name}.','withhold',{}),(line,'withhold',{'external':'no'})]
        for text,decision,flags in variants:
            src={'id':source,'body_html':'<p>'+text+'</p>',**flags}
            rows.append({'question':question,'sources':[src],'profile':'external' if flags.get('external')=='no' else 'internal','key':key(decision,prop if decision=='complete' else None,[line] if decision=='complete' else []),'mechanism':'Explicit local identity gloss is not admitted for initials/title/surname/pronoun/document reference; ambiguity and quoted scope cannot expand identity','protected_operation':'Unique source-scoped binding with exact declaration witness; writer/reporter/actor remain separate'})
    # Explicit speaker is distinct from a document writer; unsupported Nixon expansion stays withheld.
    for text,ref,referent,decision in [(f'"I inspected the quay," said {name}.','I',name,'complete'),('RN instructed the delegation.','RN','Richard Nixon','withhold')]:
        q=f'Who does the pronoun "{ref}" refer to in source {source}?' if ref=='I' else f'To whom does "{ref}" refer in source {source}?'
        prop={'relation':'documentary_coreference','pronoun':'i','referent':referent,'source_id':source,'binding':'single_attributed_speech_turn'}
        rows.append({'question':q,'sources':[{'id':source,'body_html':'<p>'+text+'</p>'}],'key':key(decision,prop if decision=='complete' else None,[text] if decision=='complete' else []),'mechanism':'Quoted speaker versus writer and unresolved initials','protected_operation':'Preserve existing named-speaker binding; no external RN expansion'})
    return rows
if __name__=='__main__':programme('SASQUATCH',build(),build(True),'tools/cryptid_sasquatch_packets.py',2026112505)
