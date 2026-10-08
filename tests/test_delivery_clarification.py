import json
from mplpb_combined import ledger as L, reader as R, provenance_gate as G
from mplpb_combined.record import upsert_meta, compute_hash
from tests.support import LedgerTest, WHEN


class TestDeliveryClarification(LedgerTest):
    def restricted(self, authorship='declared-human'):
        return self.page('Dog', 'dog', body='Dog information.', external='no', source_authorship=authorship)

    def test_external_ask_and_gate_withhold_same_page(self):
        rec = self.restricted()
        for profile in (R.PROFILES['external'], R.Profile('external*', 5, True)):
            self.assertEqual(R.answer(self.root, 'dog', profile).kind, R.NOT_IN_CORPUS)
            result = G.gather(self.root, 'dog', profile)
            self.assertFalse(result.sources)
            self.assertIn('external delivery', result.excluded[0]['reason'])
        self.assertEqual(R.answer(self.root, 'dog').record.id, rec.id)
        self.assertEqual(G.gather(self.root, 'dog').sources[0]['id'], rec.id)

    def test_editing_or_removing_external_policy_breaks_seal(self):
        rec = self.restricted()
        path = self.root / rec.path
        original = path.read_text()
        for value in ('yes', ''):
            path.write_text(upsert_meta(original, 'external', value))
            led = L.Ledger(self.root)
            self.assertFalse(led.by_id[rec.id][0].intact)
            self.assertEqual(R.answer(self.root, 'dog', R.PROFILES['external']).kind, R.NOT_IN_CORPUS)
            self.assertFalse(G.gather(self.root, 'dog', R.PROFILES['external']).sources)

    def test_revise_preserves_restriction_and_unknown_authorship(self):
        old = self.restricted('unknown')
        new = L.revise(self.root, old.id, body='Updated dog information.', when=WHEN)
        self.assertEqual(new.fields['external'], 'no')
        self.assertEqual(new.fields['source-authorship'], 'unknown')
        self.assertFalse(G.gather(self.root, 'dog', R.PROFILES['external']).sources)
        self.assertEqual(L.Ledger(self.root).findings(), [])

    def test_unknown_authorship_is_visible_and_not_verified(self):
        self.restricted('unknown')
        answer = R.answer(self.root, 'dog')
        self.assertIn('Who made this source is unknown', R.render(answer))
        self.assertFalse(answer.to_dict()['source_authorship']['verified'])
        result = G.gather(self.root, 'dog')
        self.assertIn('Who made this source is unknown', G.render(result))
        self.assertFalse(result.sources[0]['source_authorship']['verified'])

    def test_authorship_field_is_sealed(self):
        rec = self.restricted('unknown')
        path = self.root / rec.path
        path.write_text(upsert_meta(path.read_text(), 'source-authorship', 'declared-human'))
        self.assertFalse(L.Ledger(self.root).by_id[rec.id][0].intact)

    def test_legacy_hashes_stay_unchanged_when_fields_absent(self):
        fields={'document-id':'T-1','scope':'dog','origin':'human','origin-depth':'0','status':'current'}
        self.assertEqual(compute_hash(fields,'Dog','Body'), compute_hash(dict(fields, external='', **{'source-authorship':'','clarify-options':''}),'Dog','Body'))

    def test_broad_dog_offers_human_choices_without_changing_return(self):
        rec = self.page('Dog','dog')
        answer = R.answer(self.root, 'what is a dog')
        self.assertEqual(answer.record.id, rec.id)
        hint = answer.to_dict()['clarification']
        self.assertEqual(hint['choices'], ['dogs in general','dog breeds','dogs as companions'])
        self.assertFalse(hint['changes_retrieval'])
        self.assertIn('not claims', hint['notice'])
        self.assertEqual(G.gather(self.root,'dog').to_dict()['clarification']['choices'], hint['choices'])

    def test_clarification_is_not_evidence_and_does_not_invent_pages(self):
        result = G.gather(self.root,'dog')
        self.assertFalse(result.sources)
        self.assertEqual(result.kind,'not_in_corpus')
        self.assertIn('clarification',result.to_dict())
        self.assertNotIn('clarification',G.gather(self.root,'dog breeds').to_dict())

    def test_author_supplied_choices_are_sealed(self):
        rec = self.page('Dog','dog', clarify_options='dog breed; dog companion')
        self.assertEqual(R.answer(self.root,'dog').to_dict()['clarification']['choices'], ['dog breed','dog companion'])
        path = self.root / rec.path
        path.write_text(upsert_meta(path.read_text(),'clarify-options','anything'))
        self.assertFalse(L.Ledger(self.root).by_id[rec.id][0].intact)

    def test_invalid_policy_is_rejected_before_writing(self):
        with self.assertRaises(ValueError):
            self.page('Dog','dog',external='maybe')
        self.assertFalse(list(self.root.rglob('*.html')))

    def test_loose_imports_use_sealed_policy_and_keep_log_valid(self):
        import importlib.util
        from pathlib import Path
        spec = importlib.util.spec_from_file_location('open_clone_test', Path(__file__).resolve().parents[1] / 'tools/open_clone.py')
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        src = self.root / 'inputs'
        src.mkdir()
        (src / 'sources.json').write_text(json.dumps([
            {'title':'Dog','body':'Dog information.','origin':'human'},
            {'title':'Cat','body':'Cat information.'}]))
        dest = self.root / 'output'
        rows = tool.clone(src,dest)
        self.assertTrue(all(not x['origin_verified'] and not x['external'] for x in rows))
        self.assertEqual(L.Ledger(dest).findings(), [])
        for question in ('dog','cat'):
            self.assertEqual(R.answer(dest, question, R.PROFILES['external']).kind, R.NOT_IN_CORPUS)
            self.assertFalse(G.gather(dest, question, R.PROFILES['external']).sources)
        self.assertEqual(R.answer(dest,'cat').to_dict()['source_authorship']['status'],'unknown')
