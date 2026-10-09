"""Topic-carrying conversational exploration; never a source of ledger claims."""
import re
from tools import deterministic_mind as M
from tools import reduction as R

VERSION = 'idea-chat-v1'

def topic_request(message):
    if message.casefold().strip(' ?.!,') in {'can we talk about nothing','talk about nothing','chat about nothing'}:return None
    return re.fullmatch(r"(?:(?:can we |let's |lets )?(?:(?:chat|talk) about|discuss)|explore(?: an idea about| an idea| the idea of)?)\s+(.+?)[?.!]*", message.strip(), re.I)

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
        body = f'Keeping {subject} in mind: I don’t have a verified answer to that here. What is your own guess or starting point? We can explore it as an idea, or you can choose serious mode to check loaded sources.'
    else:
        body = f'You said: “{message[:240]}”\n\nHow does that shape your idea about {subject}; what would you like to develop next?'
    return M.reply('conversation', body, None, 'IDEA-EXPLORE', authority='conversation_structure',
                   suggestions=['tell me more', 'what if things were different?', 'just chat'],
                   response_structure={'intent':'casual_idea_exploration','factual_claims':False,'mplpb_supported':False,'subject':subject,'engine':VERSION})
