#!/usr/bin/env node
// Optional browser-agent CLI. No answer-generation layer: always return MPLPB data.
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

function usage() {
 return 'Usage: node tools/mplpb_agent_bridge.mjs <GitHub-repo-or-live-site-URL> (--handshake | --question TEXT | --chat TEXT | --pages | --read PAGE) [--corpus KEY] [--session ID] [--profile-dir PATH] [--suggest] [--allow-network] [--auto-wiki]';
}
function siteFrom(url) {
 const u = new URL(url);
 if (u.protocol !== 'https:' || u.username || u.password) throw Error('Use a public HTTPS URL');
 if (u.hostname === 'github.com') {
  const parts = u.pathname.split('/').filter(Boolean);
  if (parts.length < 2) throw Error('GitHub repository URL requires owner and repository');
  return 'https://' + parts[0] + '.github.io/' + parts[1] + '/';
 }
 return u.origin + u.pathname.replace(/\/?$/, '/');
}
function argsOf(argv) {
 if (argv.includes('--help') || argv.length === 0) return {help:true};
 const opts={url:argv[0]};
 const allowed = new Set(['handshake','question','chat','pages','read','corpus','session','profile-dir','suggest','allow-network','auto-wiki']);
 for (let i=1;i<argv.length;i++) {
  const key=argv[i].replace(/^--/,'');
  if (!argv[i].startsWith('--') || !allowed.has(key)) throw Error('Unknown argument '+argv[i]);
  if (['handshake','pages','suggest','allow-network','auto-wiki'].includes(key)) opts[key]=true;
  else {if (i+1>=argv.length || argv[i+1].startsWith('--')) throw Error('Missing value for --'+key);opts[key]=argv[++i];}
 }
 const modes=['handshake','question','chat','pages','read'].filter(k=>opts[k]!==undefined);
 if (modes.length!==1) throw Error('Choose exactly one mode: '+modes.join(', '));
 if (!opts.handshake && !opts.corpus) throw Error('Live calls require --corpus');
 return opts;
}
async function run() {
 const o=argsOf(process.argv.slice(2));
 if(o.help){console.log(usage());return;}
 const site=siteFrom(o.url);
 if(o.handshake) {
  const response=await fetch(new URL('.well-known/mplpb.json',site),{redirect:'error'});
  if (!response.ok) throw Error('Handshake HTTP '+response.status);
  const manifest=await response.json();
  console.log(JSON.stringify(manifest,null,2));return;
 }
 let chromium;
 try{({chromium}=await import('playwright'));}catch{throw Error('Install optional browser support: npm install playwright && npx playwright install chromium');}
 const temporary=!o['profile-dir'];
 const dir=o['profile-dir']||await mkdtemp(join(tmpdir(),'mplpb-agent-'));
 let context;
 try{
  context=await chromium.launchPersistentContext(dir,{headless:true});
  const page=context.pages()[0]||await context.newPage();
  await page.goto(site,{waitUntil:'domcontentloaded',timeout:120000});
  await page.waitForFunction(()=>Boolean(window.MPLPB),null,{timeout:120000});
  const response=await page.evaluate(async o=>{
   const api=window.MPLPB;
   const ready=await api.ready();
   if(!ready.ok)return ready;
   if(o.pages)return api.listPages({corpus:o.corpus,profile:'external'});
   if(o.read)return api.readPage(o.read,{corpus:o.corpus,profile:'external'});
   return api.relay(o.question||o.chat,{
    corpus:o.corpus,mode:o.chat?'chat':'query',
    ...(o.session?{session:o.session}:{}),
    ...(o.suggest?{includeSuggestions:true}:{}),
    ...(o['allow-network']?{allowNetwork:true}:{}),
    ...(o['auto-wiki']?{autoWiki:true}:{}),
   });
  },o);
  console.log(JSON.stringify(response,null,2));
  if(!response.ok)process.exitCode=2;
 }finally{
  if(context)await context.close();
  if(temporary)await rm(dir,{recursive:true,force:true});
 }
}
run().catch(e=>{console.error(e.message);process.exitCode=1;});
