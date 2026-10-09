"""Topic-carrying conversational exploration; never a source of ledger claims."""
import re
from tools import deterministic_mind as M
from tools import reduction as R
from tools import question_frames as PF

VERSION = 'idea-chat-v4'

def topic_request(message):
    subject=PF.overview_subject(message)
    return (None,subject) if subject else None


def handle(message, memory):
    request = topic_request(message)
    state = memory.get('idea_chat', {})
    if request:
        subject = request[1].strip()
        if subject.casefold() in {'it', 'that', 'this', 'more'} and state.get('subject'):
            subject = state['subject']
        if len(subject) > 180:
            return M.reply('conversation', 'Give me a shorter topic name; then we can explore your idea.', None, 'IDEA-LIMIT', authority='conversation_structure')
        state = {'subject': subject, 'turn': 0}
        memory['idea_chat'] = state
    if not state:
        return None
    subject = state['subject']
    key = message.casefold().strip(' ?.!,')
    state['turn'] += 1
    if request:
        body = f'Let’s explore {subject}. What interests you about it; a question, a possibility, or something you want to create?'
    elif key in {'tell me more', 'go on', 'any ideas', 'explore an idea', 'yes', 'sure'}:
        body = R.wording([
            f'For {subject}, try an imaginary change: what would you add, remove, or make completely different?',
            f'Let’s give your idea about {subject} a purpose. Who would it be for, and what would you want it to do?',
            f'Imagine your idea about {subject} worked. What would be different? Then we can look at what might get in the way.'
        ], 'idea_prompt', state['turn'])[0]
    elif key in {'why', 'how', 'how so', 'why not'}:
        body = f'I’m using questions to develop your idea about {subject}. We can start with your goal, consider an alternative, and examine what would have to be true for it to work.'
    elif key.startswith(('what if ', 'imagine ', 'suppose ')):
        body = f'Let’s treat that as an imagined possibility about {subject}, rather than an established fact. What would follow from your assumption? What might prevent it?'
    elif re.match(r'^(?:what|who|when|where|how|is|are|does|do|can|will)\b',key) or message.endswith('?'):
        referential=bool(re.search(r'\b(?:it|its|they|their|them|this|that)\b',key))
        body = (f'About {subject}: ' if referential else '')+'I don’t have a verified answer from the available source text. We can look for a source, or explore it as an idea without treating it as a fact.'
    else:
        body = f'You said: “{message[:240]}”\n\nHow does that shape your idea about {subject}; what would you like to develop next?'
    return M.reply('conversation', body, None, 'IDEA-EXPLORE', authority='conversation_structure',
                   suggestions=['Tell me more about '+subject, 'Search '+subject],
                   response_structure={'intent':'casual_idea_exploration','factual_claims':False,'mplpb_supported':False,'subject':subject,'engine':VERSION})


def brainstorm(message,memory,context=None):
    """Compose exploratory transformations around any supplied topic; no facts."""
    text=PF.normalize(message).strip(' .!?')
    match=re.fullmatch(r"(?:(?:let's|lets|let us|help me) )?brainstorm(?: ideas)?(?: (?:for|about|on))?(?: (.{1,160}))?",text,re.I)
    if not match:return None
    subject=match[1] or memory.get('idea_chat',{}).get('subject') or (context or {}).get('title')
    if subject and subject.casefold() in {'it','this','that'}:
        subject=memory.get('idea_chat',{}).get('subject') or (context or {}).get('title')
    if not subject:
        return M.reply('conversation','Absolutely. What would you like to brainstorm; a project, a story, or a problem?',context,'BRAINSTORM-TOPIC',authority='conversation_structure',
                       response_structure={'intent':'casual_idea_exploration','factual_claims':False,'mplpb_supported':False})
    prior=memory.get('idea_chat',{})
    turn=prior.get('brainstorm_turn',0)+1 if prior.get('subject')==subject else 1
    memory['idea_chat']={'subject':subject,'turn':turn,'brainstorm_turn':turn}
    operations=[('simplify','Start with the smallest useful version of ', '; choose one thing it should do well.'),
                ('combine','Combine ', ' with an unexpected theme; what would the combination change?'),
                ('perspective','Explore ', ' from a newcomer’s point of view; what would make the first step inviting?'),
                ('reverse','Reverse one assumption about ', '; what possibility does that open?'),
                ('constraint','Give ', ' one playful constraint; what could you create inside it?'),
                ('prototype','Sketch a quick example of ', '; use it to discover what needs changing.')]
    chosen=[operations[((turn-1)*3+i)%len(operations)] for i in range(3)]
    body='Let’s brainstorm '+subject+'. Here are three possibilities:\n\n'+'\n'.join(str(i)+'. '+start+subject+end for i,(_,start,end) in enumerate(chosen,1))
    if memory.get('emotional',{}).get('style')!='listen':body+='\n\nWhich direction would you like to develop?'
    return M.reply('conversation',body,context,'BRAINSTORM-CONSTRUCT',authority='conversation_structure',
                   suggestions=['Brainstorm '+subject,'Tell me about '+subject,'Search '+subject],
                   response_structure={'intent':'casual_idea_exploration','subject':subject,'factual_claims':False,'mplpb_supported':False,
                                       'construction':{'version':VERSION,'rules':['transformation + user_topic + exploration_prompt'],'operations':[x[0] for x in chosen],'turn':turn}})
