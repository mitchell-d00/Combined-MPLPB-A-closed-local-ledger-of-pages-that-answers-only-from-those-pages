"""Contextual navigation suggestions, not evidence or executable user instructions."""

def guidance(result):
    structure=result.get('response_structure',{})
    subject=structure.get('subject') or (result.get('context') or {}).get('title')
    actions=[]
    def add(label,request,mode='send'):
        if (request or mode=='draft') and not any(a['request']==request for a in actions):
            actions.append({'label':label,'request':request,'mode':mode})
    mode=result.get('reference_topic')
    if mode:
        title=mode.title()+' · '+(result.get('headword') or 'choose a word')
        hint='Meanings stay separate. Choose another word or browse the available senses.'
        for request in result.get('suggestions',[]):
            if request in {'next senses','previous senses'}:add(request.capitalize(),request)
        word=result.get('headword')
        if word:add('Synonyms' if mode=='dictionary' else 'Definitions',('synonyms ' if mode=='dictionary' else 'define ')+word)
        add('Another word','synonyms ' if mode=='thesaurus' else 'define ','draft')
        add('Leave reference','leave '+mode)
    elif result.get('kind') in {'ambiguous','clarify','conflict'} or structure.get('branch_candidates'):
        title='Choose what you mean'
        hint='Choose one of the offered meanings, or write a more specific request.'
        for request in result.get('suggestions',[])[:4]:add(request,request)
        add('Clarify my question','','draft')
    elif result.get('source_exhausted'):
        title='More about '+str(subject or 'this topic')
        hint='The available text has run out. Search can contact the selected online source.'
        if subject:add('Find more sources','search '+subject)
        add('Choose another topic','Tell me about ','draft')
    elif result.get('sources') and result.get('authority') not in {'system_description','lexical_reference'}:
        title='Explore '+str(subject or 'these sources')
        hint='Choose a follow-up, or type your own. Each answer still needs supporting text.'
        if result.get('has_more_source_text'):add('Read more','tell me more')
        for request in result.get('suggestions',[]):
            if request.lower().startswith(('how ','why ','what ')):add(request,request)
        if result.get('context') or structure.get('intent')=='source_exploration':add('View source text','show source')
        add('Ask a question','','draft')
        add('Choose another topic','Tell me about ','draft')
    elif result.get('kind') in {'unsupported','not_in_corpus','unknown_relation','reference_missing'}:
        title='Find a supported answer'
        hint='Try a more specific question or find another source. A suggestion is not a promise of an answer.'
        for request in result.get('suggestions',[])[:3]:add(request,request)
        if subject:add('Search for sources','search '+subject)
        add('Rephrase my question','','draft')
    else:
        title='Where would you like to go next?'
        hint='Choose a suggestion or write naturally. You can switch topics at any time.'
        for request in result.get('suggestions',[])[:3]:add(request,request)
        add('Explore a topic','Tell me about ','draft')
        add('Look up a word','topic dictionary')
    # Empty drafts intentionally clear/focus the composer rather than send a command.
    if not any(a['mode']=='draft' for a in actions):
        actions.append({'label':'Ask something else','request':'','mode':'draft'})
    return {'title':title,'hint':hint,'actions':actions[:6]}
