import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from urllib.parse import parse_qs, urlsplit

from test_tools.generate_open_data_seeds import main


class OpenDataSeedsTests(unittest.TestCase):
    def output(self, *args):
        buffer = StringIO()
        with redirect_stdout(buffer):
            main(args)
        return buffer.getvalue()

    def test_replay_and_catalog_bounds(self):
        text = self.output('--seed', '2a', '--count', '4')
        self.assertEqual(text, self.output('--seed', '00002A', '--count', '4'))
        plan = json.loads(text)
        self.assertEqual([draw['draw'] for draw in plan['draws']], [1, 2, 3, 4])
        for draw in plan['draws']:
            urls = [urlsplit(url) for url in draw['candidates']]
            if draw['catalog'] == 'Wikidata':
                self.assertEqual(len({url.path for url in urls}), 8)
                for url in urls:
                    self.assertEqual(url.hostname, 'www.wikidata.org')
                    self.assertRegex(url.path, r'^/wiki/Special:EntityData/Q[0-9]+\.json$')
            else:
                self.assertEqual(len(urls), 3)
                self.assertEqual(draw['selection_key'], f"{plan['seed']}:{draw['draw']}")
                for url in urls:
                    self.assertEqual(url.hostname, 'earthquake.usgs.gov')
                    params = parse_qs(url.query)
                    self.assertLess(params['starttime'], params['endtime'])
                    self.assertEqual(params['format'], ['geojson'])

    def test_fresh_seed_and_copyable_prompt(self):
        first, second = (json.loads(self.output()) for _ in range(2))
        self.assertNotEqual(first['seed'], second['seed'])
        self.assertNotEqual(first['draws'], second['draws'])
        prompt = self.output('--seed', first['seed'], '--prompt')
        self.assertIn('Never give the engine the answer key', prompt)
        self.assertTrue(prompt.endswith(json.dumps(first, indent=2) + '\n'))
