import argparse
import base64
import hashlib
import json
import ssl
import subprocess
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser()
p.add_argument('--root',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--preview-dir')
p.add_argument('--live-updated',action='store_true')
args=p.parse_args()
import sys
sys.path.insert(0,str(args.root.resolve()))
from tools.browser_release_smoke import preview_server,verify

url='https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/'
context=ssl.create_default_context()
assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
with urllib.request.urlopen(url,context=context,timeout=120) as response:
    assert urlsplit(response.url).hostname==urlsplit(url).hostname
    der=response.fp.raw._sock.getpeercert(binary_form=True)
cert=x509.load_der_x509_certificate(der)
key=cert.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
pin=base64.b64encode(hashlib.sha256(key).digest()).decode()
check=subprocess.run(['curl','--fail','--silent','--show-error','--pinnedpubkey','sha256//'+pin,
                      '--output','/dev/null','--write-out','%{http_code}',url],text=True,capture_output=True,timeout=120)
check.check_returncode();assert check.stdout=='200'
receipt={'host':urlsplit(url).hostname,'url':url,'tls_hostname_and_chain_verified':True,
         'curl_http_status':check.stdout,'spki_sha256_base64':pin,
         'certificate_sha256':hashlib.sha256(der).hexdigest(),'issuer':cert.issuer.rfc4514_string(),
         'approach':'Verified TLS and curl pinned public key, then explicit matching Chromium SPKI; no global TLS bypass.',
         'live_updated':args.live_updated,'engine_checks':[]}


def check_engine(page,label):
    result=page.evaluate('''async () => {
      const r=await window.MPLPB.query('What is Dungeons and Dragons?',{corpus:'logic'});
      if(!r.ok) throw new Error(JSON.stringify(r));
      return r.data.reader.answer_contract.code_sha256;
    }''')
    matched={}
    for name in ['pipeline.py','documentary_instruction.py','source_attribution.py']:
        expected=hashlib.sha256((args.root/'mplpb_answers'/name).read_bytes()).hexdigest()
        candidates=[v for k,v in result.items() if k==name or k.endswith('/'+name)]
        assert candidates and all(v==expected for v in candidates),(label,name,candidates,expected)
        matched[name]=expected
    receipt['engine_checks'].append({'surface':label,'module_hashes':matched})
    print('PASS deployed module hashes' if label=='published-live' else 'PASS candidate module hashes',flush=True)


start=time.monotonic()
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(headless=True,args=[
        '--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors-spki-list='+pin])
    try:
        c=browser.new_context(ignore_https_errors=False)
        try:
            page=c.new_page();verify(page,url,args.live_updated)
            if args.live_updated:check_engine(page,'published-live')
        finally:c.close()
        if args.preview_dir:
            with preview_server(args.preview_dir) as preview:
                c=browser.new_context(ignore_https_errors=False)
                try:
                    page=c.new_page();verify(page,preview,True);check_engine(page,'candidate-preview')
                finally:c.close()
    finally:browser.close()
receipt.update(published_live='PASS',candidate_preview='PASS' if args.preview_dir else 'NOT_RUN',
               seconds=round(time.monotonic()-start,3))
args.output.write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS verified-host browser checks',flush=True)
