"""Run retained browser verifier with an explicit installed Chromium binary."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from tools.browser_release_smoke import verify, preview_server
p=argparse.ArgumentParser();p.add_argument('--dist',required=True);p.add_argument('--output',required=True);p.add_argument('--chromium',default='/usr/bin/chromium');args=p.parse_args()
results=[]
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for arm in ('published-baseline','candidate-preview'):
        context=browser.new_context(ignore_https_errors=False)
        try:
            if arm=='published-baseline':
                report=verify(context.new_page(),'https://mitchell-d00.github.io/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/',False)
            else:
                with preview_server(args.dist) as url:report=verify(context.new_page(),url,True)
            results.append({'arm':arm,'status':'passed','report':report})
        except Exception as exc:
            results.append({'arm':arm,'status':'failed','error':type(exc).__name__+': '+str(exc)})
        finally:context.close()
    browser.close()
with Path(args.output).open('x') as stream:json.dump(results,stream,indent=2)
if any(r['status']!='passed' for r in results):raise SystemExit(1)
