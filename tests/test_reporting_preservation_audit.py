"""A representation migration must not hide changes in source-supported claims."""
import copy
import unittest
from tools.cryptid_semantic_preservation_v1 import validate, recovery_ok


class ReportingPreservationAuditTests(unittest.TestCase):
    def raw(self):
        text='Rina Sable did not say, “Oren Keel did not write the slate index.”'
        prop={'relation':'source_attributed_report_content','reporter':'Rina Sable','author':'Oren Keel','object':'the slate index','outer_negative':True,'inner_negative':None,'inner_polarity':'unasserted','embedded_content_negative':True}
        citation={'source_id':'R','hash':'sha256:unit-control','body_start':0,'body_end':len(text),'quote':text}
        return {'answer':{'claims':[{'proposition':prop,'citations':[citation],'qualifiers':['Source-scoped only.']}]},'records':[{'id':'R','hash':'sha256:unit-control','body':text}]}

    def test_literal_negation_is_checked_without_asserting_its_truth(self):
        raw=self.raw();before=copy.deepcopy(raw);view,errors,removed=validate(raw)
        self.assertEqual(errors,[]);self.assertEqual(removed,1)
        self.assertIsNone(view['claims'][0]['proposition']['inner_negative'])
        self.assertEqual(view['claims'][0]['proposition']['inner_polarity'],'unasserted')
        self.assertEqual(raw,before)

    def test_wrong_added_polarity_is_rejected(self):
        raw=self.raw();raw['answer']['claims'][0]['proposition']['embedded_content_negative']=False
        self.assertIn('additive_embedded_polarity_not_uniquely_source_witnessed',validate(raw)[1])

    def test_bad_source_coordinates_are_rejected(self):
        raw=self.raw();raw['answer']['claims'][0]['citations'][0]['body_end']-=1
        self.assertIn('invalid_exact_citation',validate(raw)[1])

    def test_legacy_assertion_changes_are_not_normalized_away(self):
        old=self.raw();changed=copy.deepcopy(old);changed['answer']['claims'][0]['proposition']['inner_negative']=True
        self.assertNotEqual(validate(old)[0],validate(changed)[0])

    def test_unverified_recovery_is_not_accepted(self):
        raw=self.raw();after=raw['answer'];after.update(question='Q',kind='supported_answer',answer_supported=True,verification={'truth_verified':False})
        claim=after['claims'][0];claim['source_support_established']=False
        criterion={'question':'Q','required_legacy_proposition':{'outer_negative':True},'complete_witness':claim['citations'][0]['quote'],'qualification_fragments':['Source-scoped']}
        self.assertFalse(recovery_ok({'claims':[],'answer_supported':False},after,criterion))
