import unittest
from tools import question_frames as F
from tools import idea_chat as I

class QuestionFrameTests(unittest.TestCase):
    def test_common_overview_frames_are_topic_independent(self):
        patterns=['tell me about {}','Can you tell me about {}?','Could you please tell me about {}?',
                  'Would you give me an overview of {}?','Tell me a little about {}','tell me something about {}',
                  'What do you know about {}?','What can you tell me about {}?',
                  'Please describe {}','explain {}','summarize {}','summarise {}',
                  'Help me understand {}','Teach me about {}','I want to learn about {}',
                  "I'm interested in {}","Let's chat about {}",'Can we discuss {}?',
                  'Will you talk to me about {}?','Give me some facts on {}','Explore an idea about {}', 'Would you mind telling me about {}?',
                  'Could you give me some information about {}?', "I'd like to know about {}",
                  'Can I ask you about {}?', 'Tell me a bit more about {}',
                  'Do you have info on {}?', 'What about {}?', 'Would you mind explaining {}?']
        for topic in ['the Moon','electric motors','a banana']:
            for pattern in patterns:
                text=pattern.format(topic)
                self.assertIsNotNone(I.topic_request(text),text)
                self.assertEqual(I.topic_request(text)[1],topic,text)
    def test_polite_questions_preserve_question_type(self):
        for text,expected in [('Can you tell me how big it is?','how big is it?'),
                              ('Could you explain why it moves?','why it moves?'),
                              ("I'd like to know who built it",'who built it'),
                              ('Do you know when it formed?','when it formed?'),
                              ('I was wondering where it is','where is it'),
                              ("What's its diameter?",'what is its diameter?')]:
            self.assertEqual(F.normalize(text),expected)
            self.assertFalse(F.frame(text)['normalization_is_evidence'])
    def test_self_chat_and_commands_are_not_source_requests(self):
        for text in ['Tell me about yourself','say potato','I feel sad','Can we talk about nothing?', 'no jokes','what about its size?',"what about the Moon's diameter?"]:
            self.assertIsNone(I.topic_request(text),text)
