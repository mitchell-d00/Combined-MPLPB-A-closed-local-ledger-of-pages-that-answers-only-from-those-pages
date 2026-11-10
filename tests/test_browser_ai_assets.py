"""Pinned optional browser assets and faithful embedding; no model weights downloaded."""
import hashlib
import json
import re
from pathlib import Path
import shutil
import tempfile
import unittest
from tools import build_ai_assets as A


class BrowserAIAssetsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def test_reconstruct_pinned_runtime_without_network(self):
        raw=A.runtime()
        manifest=json.loads((A.ROOT/'assets/ai/manifest.json').read_text())['runtime']
        self.assertEqual(hashlib.sha256(raw).hexdigest(),manifest.get('local_patch',{}).get('output_sha256',manifest['uncompressed_sha256']))
        self.assertIn(b'CreateMLCEngine',raw)
        result=A.build(self.root/'site')
        self.assertFalse(result['models_downloaded']);self.assertFalse(result['paid_service_configured'])
        self.assertEqual((self.root/'site/webllm.mjs').read_bytes(),raw)

    def test_changed_patch_fails_before_build(self):
        shutil.copytree(A.ROOT/'assets',self.root/'assets')
        path=self.root/'assets/ai/patches/webgpu-device-limits-v1.json'
        path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'patch differs from pin'):A.runtime(self.root)

    def test_stale_model_runtime_pin_fails_before_delivery(self):
        shutil.copytree(A.ROOT/'assets',self.root/'assets')
        path=self.root/'assets/ai/model.json'
        model=json.loads(path.read_text());model['runtime']['sha256']='0'*64
        path.write_text(json.dumps(model))
        with self.assertRaisesRegex(ValueError,'runtime pin differs'):A.build(self.root/'site',self.root)

    def test_changed_runtime_part_fails_before_build(self):
        shutil.copytree(A.ROOT/'assets',self.root/'assets')
        part=next((self.root/'assets/ai/runtime-parts').iterdir())
        part.write_bytes(part.read_bytes()+b'x')
        with self.assertRaisesRegex(ValueError,'differs from pin'):A.runtime(self.root)

    def test_html_embedding_is_current_idempotent_and_contains_original_script_first(self):
        A.embed(check=True)
        shutil.copytree(A.ROOT/'browser',self.root/'browser',ignore=shutil.ignore_patterns('__pycache__'))
        (self.root/'index.html').write_text('<html><body><script>original()</script>\n</body></html>')
        A.embed(self.root);first=(self.root/'index.html').read_text()
        A.embed(self.root,check=True);A.embed(self.root)
        self.assertEqual((self.root/'index.html').read_text(),first)
        self.assertLess(first.index('original()'),first.index('browser-ai-helper-v1'))
        self.assertEqual(len(re.findall(r'<script>(.*?)</script>',first,re.S)),1)
        self.assertIn("document.addEventListener('DOMContentLoaded'",first)
        (self.root/'browser/ai-helper.js').write_text('changed')
        with self.assertRaisesRegex(ValueError,'stale'):A.embed(self.root,check=True)

    def test_model_and_library_locations_are_immutable_with_clear_license_and_cost(self):
        data=json.loads((A.ROOT/'assets/ai/model.json').read_text())
        self.assertRegex(data['record']['model'],r'/resolve/[0-9a-f]{40}/$')
        self.assertRegex(data['record']['model_lib'],r'/[0-9a-f]{40}/web-llm-models/')
        self.assertEqual(data['record']['integrity']['onFailure'],'error')
        self.assertTrue(data['record']['integrity']['model_lib'].startswith('sha256-'))
        self.assertIn('MIT',data['license'])
        self.assertNotIn('api_key',json.dumps(data))
        self.assertGreater(data['weights']['tensor_download_bytes'],2_000_000_000)

    def test_catalog_is_mit_only_pinned_and_defaults_to_smallest_model(self):
        catalog=json.loads((A.ROOT/'assets/ai/models.json').read_text())
        models=catalog['models']
        self.assertEqual(len(models),3)
        smallest=min(models,key=lambda m:m['weights']['tensor_download_bytes'])
        self.assertEqual(catalog['default_model_id'],smallest['model_id'])
        self.assertLess(smallest['weights']['tensor_download_bytes'],800_000_000)
        for model in models:
            self.assertEqual(model['license_spdx'],'MIT')
            self.assertRegex(model['license_source'],r'/resolve/[0-9a-f]{40}/LICENSE$')
            self.assertRegex(model['record']['model'],r'/resolve/[0-9a-f]{40}/$')
            self.assertRegex(model['record']['model_lib'],r'/[0-9a-f]{40}/web-llm-models/')
            self.assertEqual(model['record']['model_id'],model['model_id'])
            self.assertEqual(model['record']['integrity']['onFailure'],'error')
            self.assertEqual(model['record']['model'],model['weights']['url'])
        A.build(self.root/'site')
        for model in models:
            self.assertTrue((self.root/'site'/model['license_file']).exists())
        self.assertEqual(json.loads((self.root/'site/models.json').read_text()),catalog)

    def test_non_mit_catalog_or_modified_license_cannot_be_built(self):
        shutil.copytree(A.ROOT/'assets',self.root/'assets')
        path=self.root/'assets/ai/models.json';original=path.read_text();catalog=json.loads(original)
        catalog['models'][0]['license_spdx']='Apache-2.0';path.write_text(json.dumps(catalog))
        with self.assertRaisesRegex(ValueError,'Only MIT'):A.build(self.root/'site',self.root)
        path.write_text(original)
        notice=self.root/'assets/ai'/catalog['models'][0]['license_file'];notice.write_text('MIT License\nmodified')
        with self.assertRaisesRegex(ValueError,'notice differs from pin'):A.build(self.root/'site',self.root)
