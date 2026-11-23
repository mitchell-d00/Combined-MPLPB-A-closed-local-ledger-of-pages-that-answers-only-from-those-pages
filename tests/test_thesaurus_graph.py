"""Independent lexical relations remain distinct and discovery-only."""
from io import BytesIO
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
import unittest

from mplpb_work.thesaurus import build, lookup, probe
from mplpb_combined.ledger import write


class ThesaurusTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / 'wordnet.tar.gz'
        self.reference = self.root / 'reference.csv'
        self.db = self.root / 'lexicon.sqlite'
        nouns = (
            '00000001 00 n 02 canal 0 channel 0 001 @ 00000002 n 0000 | an artificial waterway\n'
            '00000002 00 n 01 waterway 0 001 ~ 00000001 n 0000 | a navigable body of water\n'
            '00000003 00 n 02 channel 0 frequency 0 000 | part of a radio band\n'
        )
        with tarfile.open(self.source, 'w:gz') as archive:
            entries = {'dict/data.noun': nouns, 'dict/data.verb': '', 'dict/data.adj': '',
                       'dict/data.adv': '', 'LICENSE': 'Mock dataset license'}
            for name, content in entries.items():
                data = content.encode()
                member = tarfile.TarInfo('WordNet-3.0/' + name)
                member.size = len(data)
                archive.addfile(member, BytesIO(data))
        self.reference.write_text('canal,channel,ditch\nchannel,frequency,ditch\n')
        build(self.db, self.source, self.reference)

    def test_senses_and_direction_are_preserved(self):
        result = lookup(self.db, 'channel')
        self.assertEqual(len(result['senses']), 2)
        self.assertFalse(result['answer_supported'])
        canal = lookup(self.db, 'canal', sense='n:00000001')['senses'][0]
        self.assertEqual(canal['synonyms'], ['channel'])
        self.assertEqual(canal['relations'], [{'kind': 'broader', 'sense': 'n:00000002',
                                               'words': ['waterway']}])
        self.assertNotIn('frequency', canal['synonyms'])
        waterway = lookup(self.db, 'waterway')['senses'][0]
        self.assertEqual(waterway['relations'][0]['kind'], 'narrower')

    def test_reference_associations_do_not_become_synonyms(self):
        result = lookup(self.db, 'canal')
        self.assertEqual(result['reference_associations'], ['channel', 'ditch'])
        self.assertEqual(result['senses'][0]['synonyms'], ['channel'])
        self.assertEqual(lookup(self.db, 'inventedzz')['senses'], [])
        with self.assertRaises(ValueError):
            lookup(self.db, 'canal', sense='n:00000003')

    def test_build_preserves_existing_index(self):
        before = self.db.read_bytes()
        with self.assertRaises(FileExistsError):
            build(self.db, self.source, self.reference)
        self.assertEqual(self.db.read_bytes(), before)


    def test_scoped_probe_does_not_expand_associations_or_cross_senses(self):
        ledger = self.root / 'ledger'
        source = write(ledger, doc_id='WATER-1', title='Harbor', scope='harbor record',
                       body='The channel was dredged.', when='2026-11-23')
        result = probe(self.db, ledger, 'What happened to the canal?', 'canal', 'n:00000001')
        self.assertEqual(result['expansion'], ['channel'])
        self.assertEqual(result['expanded']['passages'][0]['source_id'], source.id)
        self.assertFalse(result['answer_supported'])
        related = probe(self.db, ledger, 'What happened to the canal?', 'canal', 'n:00000001',
                        relation='broader')
        self.assertEqual(related['expansion'], ['waterway'])
        with self.assertRaises(ValueError):
            probe(self.db, ledger, 'What happened to the canal?', 'canal', None)

    def test_relation_span_search_finds_exact_neighbor_without_admitting_proof(self):
        ledger = self.root / 'ledger'
        write(ledger, doc_id='DECOY', title='Catalog', scope='harbor record',
              body='The canal inspections are indexed by year.', when='2026-11-23')
        source = write(ledger, doc_id='WATER-1', title='Harbor', scope='harbor record',
                       body='The waterway overflowed the banks.', when='2026-11-23')
        result = probe(self.db, ledger, 'What do the canal inspections establish?', 'canal', 'n:00000001',
                       relation='broader', max_passages=1)
        self.assertEqual(result['edge_hits'][0]['source_id'], source.id)
        self.assertEqual(result['edge_hits'][0]['matched_terms'], ['waterway'])
        self.assertFalse(result['edge_hits'][0]['answer_supported'])
